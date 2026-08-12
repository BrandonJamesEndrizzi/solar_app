"""Build the HTML body of the report email."""

import html


def get_html_email_body(disclaimer, image_intro, image_cid, solar_summary,
                        news_summary):
    """Return the HTML body, omitting any section that has no content."""
    sections = [f"<p>{html.escape(disclaimer)}</p>"]

    if solar_summary:
        sections.append(f"<p>{html.escape(solar_summary)}</p>")

    if image_cid:
        sections.append(f"<p>{html.escape(image_intro)}</p>")
        sections.append(f'<img src="cid:{html.escape(image_cid)}" alt="The Sun">')
        sections.append(
            "<p>See the attachments for more spectral images of the Sun.</p>"
        )

    if news_summary:
        sections.append("<p>Here is some recent news from the last week.</p>")
        sections.append(f"<p>{html.escape(news_summary)}</p>")

    body = "\n            ".join(sections)
    return f"""<html>
        <body>
            {body}
        </body>
    </html>"""
