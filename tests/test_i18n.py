"""Localization contract for the English and Brazilian Portuguese interfaces."""

import unittest

from i18n import (
    EN, PT_BR, SUPPORTED_CHOICES, effective_language, translate,
    translate_failure,
)


class LocalizationTests(unittest.TestCase):
    def test_catalogs_have_identical_keys_and_nonempty_translations(self):
        self.assertEqual(set(EN), set(PT_BR))
        self.assertTrue(all(text.strip() for text in EN.values()))
        self.assertTrue(all(text.strip() for text in PT_BR.values()))
        self.assertEqual(tuple(SUPPORTED_CHOICES), ("en", "pt_BR"))

    def test_explicit_choices_and_legacy_auto_default_to_english(self):
        self.assertEqual(effective_language("auto", "pt_BR"), "en")
        self.assertEqual(effective_language("en", "pt_BR"), "en")
        self.assertEqual(effective_language("pt_BR", "en_US"), "pt_BR")
        self.assertEqual(effective_language("invalid"), "en")

    def test_format_tokens_match_across_languages(self):
        import string

        formatter = string.Formatter()
        for key in EN:
            en_fields = {field for _, field, _, _ in formatter.parse(EN[key]) if field}
            pt_fields = {field for _, field, _, _ in formatter.parse(PT_BR[key]) if field}
            self.assertEqual(en_fields, pt_fields, key)
        self.assertIn("3 locais", translate(
            "pt_BR", "destination_multiple", count=3, folders="A, B, C"
        ))

    def test_technical_error_details_are_preserved(self):
        error = "No audio stream found: recording.mkv"
        self.assertEqual(translate_failure("en", error), error)
        self.assertEqual(
            translate_failure("pt_BR", error),
            "Nenhuma faixa de áudio encontrada: recording.mkv",
        )
        self.assertEqual(
            translate_failure("pt_BR", "Unknown FFmpeg failure"),
            "Unknown FFmpeg failure",
        )

    def test_completion_messages_use_natural_portuguese_plurals(self):
        self.assertEqual(
            translate("pt_BR", "complete", completed=1),
            "Concluído: 1 arquivo convertido.",
        )
        self.assertEqual(
            translate("pt_BR", "complete", completed=3),
            "Concluído: 3 arquivos convertidos.",
        )
        self.assertEqual(
            translate("pt_BR", "cancelled", completed=1),
            "Cancelado. 1 arquivo concluído.",
        )
