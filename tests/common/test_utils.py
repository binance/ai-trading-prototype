from aitradingprototype.common.utils import split_line


def test_valid_split_line_sentiment():
    headlines_sentiments = [
        '"NewsAPI","1640310400000","1630310400000","Test Headline","bullish"',
        '"NewsAPI","1640310400000","1630310400000","Test, Headline","bullish"',
        '"NewsAPI","1640310400000","1630310400000","Test"Headline"","bullish"',
    ]
    for hl in headlines_sentiments:
        (
            collected_source,
            collected_time,
            published_time,
            headline,
            sentiment,
        ) = split_line(hl)
        assert collected_source == "NewsAPI"
        assert collected_time == "1640310400000"
        assert published_time == "1630310400000"
        assert (
            True
            if headline == "Test Headline"
            or headline == "Test, Headline"
            or headline == 'Test"Headline"'
            else False
        )
        assert sentiment == "bullish"


def test_invalid_split_line_sentiment():
    headlines_sentiments = (
        '"NewsAPI","1640310400000","1630310400000","Test, Headline","bullish"'
    )
    # If the length of the list is greater than 3, it means that the line was not split correctly
    assert True if len(split_line(headlines_sentiments)) > 3 else False
