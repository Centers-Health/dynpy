from dynpy.testing_utils.hx_requests import add_middleware_to_request


def test_gives_the_request_a_readable_session(rf):
    request = add_middleware_to_request(rf.get("/"))

    assert request.session.get("anything") is None
