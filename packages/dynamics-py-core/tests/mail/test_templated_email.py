from dynpy.mail.templated_email import TemplatedEmail


def test_sends_an_email(mailoutbox):
    email = TemplatedEmail(
        subject="subject",
        template_name="tests/dummy_email_template.html",
        context={"context_var": "context_val"},
        to=["person@email.com"],
    )

    email.send()

    assert len(mailoutbox) == 1


def test_defaults_email_body_to_plain_text_version_of_template(mailoutbox):
    email = TemplatedEmail(
        subject="subject",
        template_name="tests/dummy_email_template.html",
        context={"context_var": "context_val"},
        to=["person@email.com"],
    )

    email.send()
    body = mailoutbox[0].body

    assert "Purple text div" in body
    # Basic check to make sure HTML tags are stripped
    assert ">" not in body
    assert "<" not in body


def test_uses_plain_text_body_if_one_is_provided(mailoutbox):
    email = TemplatedEmail(
        subject="subject",
        template_name="tests/dummy_email_template.html",
        context={"context_var": "context_val"},
        to=["person@email.com"],
        plain_text_body="some plain text",
    )

    email.send()
    body = mailoutbox[0].body

    assert "some plain text" in body


def test_templated_email_sends_attached_file(mailoutbox, test_file):
    email = TemplatedEmail(
        subject="subject",
        template_name="tests/dummy_email_template.html",
        context={"context_var": "context_val"},
        to=["person@email.com"],
        plain_text_body="some plain text",
        attachments=[test_file],
    )

    email.send()
    attachments = mailoutbox[0].attachments

    # there is an automatic image attachment, so 1 file + 1 image
    assert len(attachments) == 2
