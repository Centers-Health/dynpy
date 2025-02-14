import cssutils
from bs4 import BeautifulSoup
from dynpy.mail.templated_email import TemplatedEmailBootstrap


def test_converts_template_styles_to_inline(mailoutbox):
    email = TemplatedEmailBootstrap(
        subject="subject",
        template_name="tests/dummy_email_template.html",
        context={"context_var": "context_val"},
        to=["person@email.com"],
    )

    email.send()

    html_body = mailoutbox[0].alternatives[0][0]
    soup = BeautifulSoup(html_body, features="html.parser")
    purple_elem = soup.select(".purple")[0]
    purple_elem_style = cssutils.parseStyle(purple_elem["style"])
    assert purple_elem_style["color"] == "purple"
