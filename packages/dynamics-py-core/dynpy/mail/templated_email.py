from dataclasses import dataclass
from email.mime.image import MIMEImage
from typing import List, Optional

from django.conf import settings
from django.contrib.staticfiles import finders
from django.core.files.uploadedfile import UploadedFile
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from html2text import html2text


@dataclass()
class EmailImage:
    # path to the image file
    path: str
    # used as the src for the image in the email template (`<img src="cid:<content_id>"/>`)
    content_id: str

    @property
    def filename(self) -> str:
        return self.path.split("/")[-1]


class TemplatedEmail:
    """
    Class for building/sending an email with an HTML template body and images
    """

    def __init__(
        self,
        subject: str = None,
        template_name: str = None,
        context: dict = None,
        to: List[str] = None,
        plain_text_body: Optional[str] = None,
        attachments: List[UploadedFile] = None,
        images: List[EmailImage] = None,
        reply_to: List[str] | str | None = None,
    ) -> None:
        self.subject = subject or ""
        self.template_name = template_name or ""
        self.context = context or {}
        self.to = to or []
        self.plain_text_body = plain_text_body
        self.attachments = attachments or []
        self.images = images or []
        self.images.append(EmailImage("dynpy/img/centers-logo.png", "centers-header-logo"))
        if isinstance(reply_to, str):
            self.reply_to = [reply_to]
        else:
            self.reply_to = list(reply_to) if reply_to else []

    def send(self, fail_silently: bool = False):
        email = self.build_email()
        email.send(fail_silently=fail_silently)

    def build_email(self) -> EmailMultiAlternatives:
        html_body = mark_safe(render_to_string(self.template_name, self.context))
        plain_text_body = (
            self.plain_text_body if self.plain_text_body is not None else html2text(html_body)
        )

        email = EmailMultiAlternatives(
            subject=self.subject,
            body=plain_text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=self.to,
            reply_to=self.reply_to,
        )
        email.attach_alternative(html_body, "text/html")
        [
            email.attach(attachment.name, attachment.read(), attachment.content_type)
            for attachment in self.attachments
        ]

        self.attach_images(email)

        return email

    def attach_images(self, email: EmailMultiAlternatives) -> None:
        for img in self.images:
            abs_path = finders.find(img.path)
            with open(abs_path, "rb") as f:
                mime_img = MIMEImage(f.read())
                mime_img.add_header("Content-ID", f"<{img.content_id}>")
                mime_img.add_header("Content-Disposition", "inline", filename=img.filename)
                email.attach(mime_img)


class TemplatedEmailBootstrap(TemplatedEmail):
    """
    Class for building/sending an email with an HTML template body with bootstrap and images
    """

    def build_email(self) -> EmailMultiAlternatives:
        import premailer  # import here to reduce startup times

        html_body = mark_safe(render_to_string(self.template_name, self.context))
        plain_text_body = (
            self.plain_text_body if self.plain_text_body is not None else html2text(html_body)
        )
        inline_styled_body = premailer.transform(html_body)

        email = EmailMultiAlternatives(
            subject=self.subject,
            body=plain_text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=self.to,
            reply_to=self.reply_to,
        )
        email.attach_alternative(inline_styled_body, "text/html")

        self.attach_images(email)

        return email
