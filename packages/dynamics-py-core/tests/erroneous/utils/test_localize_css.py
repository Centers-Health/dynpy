from dynpy.erroneous.utils import localize_css


def test_localizes_css():
    """
    Assert that it wraps the html in a div with a set id and
    updates internal css to apply only to elements with that id
    """

    # Arrange
    test_html = """
        <body>
            <style type="text/css">
                .someclass {
                    background: red
                }
                h1 {
                    padding: 5px;
                }
            </style>
            <h1>Some text</h1>
        </body>
    """

    expected_html = """<div id="pageTemplate">
        <body>
            <style type="text/css">
                #pageTemplate .someclass {
                    background: red
                }
                #pageTemplate h1 {
                    padding: 5px;
                }
            </style>
            <h1>Some text</h1>
        </body>
    </div>"""

    # Act
    html = localize_css(test_html)

    # Assert
    assert html == expected_html
