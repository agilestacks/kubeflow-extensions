from textacy.preprocess import preprocess_text
import numbers, numpy, logging

def textacy_cleaner(text: str) -> str:
    if isinstance(text, numbers.Number) and numpy.isnan(text):
        logging.warning("Received nan instead of str")
        return "nan"

    return preprocess_text(
        text,
        fix_unicode=False,
        lowercase=True,
        transliterate=True,
        no_urls=True,
        no_emails=True,
        no_phone_numbers=True,
        no_numbers=True,
        no_currency_symbols=True,
        no_punct=True,
        no_contractions=False,
        no_accents=True)
