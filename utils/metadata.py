def get_word_count(article):
    """
    Count total words in article
    """
    return len(article.split())


def get_reading_time(article):
    """
    Estimate reading time
    Average reading speed = 200 words per minute
    """
    word_count = get_word_count(article)

    reading_time = max(1, round(word_count / 200))

    return f"{reading_time} min read"


def detect_topic(article):
    """
    Detect article category using keywords
    """

    article = article.lower()

    topic_keywords = {
        "Technology": [
            "ai", "software", "technology", "google",
            "microsoft", "apple", "startup", "robot"
        ],

        "Politics": [
            "government", "minister", "election",
            "president", "parliament", "policy"
        ],

        "Sports": [
            "match", "player", "team",
            "cricket", "football", "tournament"
        ],

        "Business": [
            "market", "stocks", "company",
            "investment", "profit", "economy"
        ],

        "Science": [
            "research", "scientist",
            "space", "experiment", "discovery"
        ]
    }

    for topic, keywords in topic_keywords.items():
        for keyword in keywords:
            if keyword in article:
                return topic

    return "General"