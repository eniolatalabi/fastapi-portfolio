"""End-to-end tests for the Social Media API over in-memory sqlite."""

def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_root_points_to_docs(client):
    body = client.get("/").json()
    assert body["status"] == "online" and body["docs"] == "/docs"


def test_register_returns_user_without_password(client):
    body = client.post("/users", json={
        "email": "a@test.dev", "password": "pw12345"}).json()
    assert body["email"] == "a@test.dev"
    assert "password" not in body
    assert body["phone_number"] is None


def test_register_with_optional_phone(register_user):
    body = register_user("p@test.dev", phone_number="+2348000000000")
    assert body["phone_number"] == "+2348000000000"


def test_duplicate_email_conflicts(client, user_one):
    response = client.post("/users", json={
        "email": user_one["email"], "password": "different"})
    assert response.status_code == 409


def test_login_returns_bearer_token(client, user_one):
    response = client.post("/login", data={
        "username": user_one["email"], "password": user_one["password"]})
    body = response.json()
    assert response.status_code == 200
    assert body["token_type"] == "bearer" and body["access_token"]


def test_login_wrong_password_is_401(client, user_one):
    response = client.post("/login", data={
        "username": user_one["email"], "password": "wrong"})
    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_login_unknown_email_is_401(client):
    response = client.post("/login", data={
        "username": "ghost@test.dev", "password": "whatever"})
    assert response.status_code == 401


def test_me_requires_authentication(client):
    assert client.get("/users/me").status_code == 401


def test_me_returns_own_profile(client, user_one, auth_one):
    body = client.get("/users/me", headers=auth_one).json()
    assert body["email"] == user_one["email"]
    assert body["id"] == user_one["id"]


def test_password_update_rotates_credentials(client, user_one, auth_one,
                                              login_as):
    response = client.put("/users/me", headers=auth_one,
                          json={"password": "newpass456"})
    assert response.status_code == 200
    old = client.post("/login", data={"username": user_one["email"],
                                      "password": user_one["password"]})
    assert old.status_code == 401
    new_headers = login_as(user_one["email"], "newpass456")
    assert client.get("/users/me", headers=new_headers).status_code == 200


def test_phone_update_via_me(client, auth_one):
    body = client.put("/users/me", headers=auth_one,
                      json={"phone_number": "+2341112223334"}).json()
    assert body["phone_number"] == "+2341112223334"


def test_email_update_to_taken_email_conflicts(client, auth_one, user_two):
    response = client.put("/users/me", headers=auth_one,
                          json={"email": user_two["email"]})
    assert response.status_code == 409


def test_deleted_account_token_is_rejected(client, auth_one):
    assert client.delete("/users/me", headers=auth_one).status_code == 204
    # The token is still cryptographically valid; the user behind it is
    # gone. This exercises the deleted-user guard in get_current_user.
    assert client.get("/users/me", headers=auth_one).status_code == 401


def test_create_post_requires_authentication(client):
    response = client.post("/posts", json={"title": "t", "content": "c"})
    assert response.status_code == 401


def test_create_post_sets_owner(client, user_one, auth_one):
    body = client.post("/posts", headers=auth_one, json={
        "title": "owned", "content": "by me"}).json()
    assert body["owner_id"] == user_one["id"]
    assert body["owner"]["email"] == user_one["email"]


def test_list_posts_returns_vote_counts(client, sample_post):
    items = client.get("/posts").json()
    assert items[0]["Post"]["title"] == "first post"
    assert items[0]["votes"] == 0


def test_get_single_post(client, sample_post):
    response = client.get(f"/posts/{sample_post['id']}")
    assert response.status_code == 200


def test_get_missing_post_is_404(client):
    assert client.get("/posts/999").status_code == 404


def test_update_post_by_non_owner_is_404(client, sample_post, auth_two):
    response = client.put(f"/posts/{sample_post['id']}", headers=auth_two,
                          json={"title": "hijacked", "content": "x"})
    assert response.status_code == 404


def test_delete_post_by_non_owner_is_404_and_post_survives(
        client, sample_post, auth_two):
    response = client.delete(f"/posts/{sample_post['id']}",
                             headers=auth_two)
    assert response.status_code == 404
    assert client.get(f"/posts/{sample_post['id']}").status_code == 200


def test_owner_can_update_and_delete_post(client, sample_post, auth_one):
    updated = client.put(f"/posts/{sample_post['id']}", headers=auth_one,
                         json={"title": "edited", "content": "new"})
    assert updated.status_code == 200
    assert updated.json()["title"] == "edited"
    deleted = client.delete(f"/posts/{sample_post['id']}",
                            headers=auth_one)
    assert deleted.status_code == 204
    assert client.get(f"/posts/{sample_post['id']}").status_code == 404


def test_vote_like_conflict_and_unlike_cycle(client, sample_post, auth_two):
    like = client.post("/vote/", headers=auth_two,
                       json={"post_id": sample_post["id"], "dir": 1})
    assert like.status_code == 201
    again = client.post("/vote/", headers=auth_two,
                        json={"post_id": sample_post["id"], "dir": 1})
    assert again.status_code == 409
    assert client.get("/posts").json()[0]["votes"] == 1
    unlike = client.post("/vote/", headers=auth_two,
                         json={"post_id": sample_post["id"], "dir": 0})
    assert unlike.status_code == 201
    assert client.get("/posts").json()[0]["votes"] == 0


def test_vote_rejects_invalid_direction(client, sample_post, auth_one):
    response = client.post("/vote/", headers=auth_one,
                           json={"post_id": sample_post["id"], "dir": 2})
    assert response.status_code == 422


def test_vote_on_missing_post_is_404(client, auth_one):
    response = client.post("/vote/", headers=auth_one,
                           json={"post_id": 999, "dir": 1})
    assert response.status_code == 404
