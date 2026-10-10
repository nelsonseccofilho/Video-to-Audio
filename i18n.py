"""Small, dependency-free catalog for the desktop UI.

Locale preference is stored by the GUI; this module only resolves and renders
strings. English remains the fallback for unknown keys or locales.
"""

from __future__ import annotations

from PyQt5.QtCore import QLocale

SUPPORTED_CHOICES = ("auto", "en", "pt_BR")

EN = {
    "window_title": "Video to Audio Converter",
    "language_label": "Language:",
    "language_auto": "Automatic (Windows)",
    "language_en": "English",
    "language_pt": "Português (Brasil)",
    "videos_label": "Videos to convert",
    "select_videos": "Select Videos",
    "remove_selected": "Remove Selected",
    "clear_list": "Clear List",
    "output_format": "Output Format:",
    "bitrate": "Bitrate:",
    "choose_folder": "Choose output folder (optional)",
    "source_folders": "Use source folders",
    "mixed_folders_hint": (
        "Videos are in different folders. To keep all audio together, "
        "you can choose one output folder. This is optional."
    ),
    "destination_custom": "Save audio to: {folder} (chosen folder)",
    "destination_none": "Save audio to: Each video's original folder (automatic)",
    "destination_single": "Save audio to: {folder} (same folder as the videos)",
    "destination_multiple": "Save audio to: Original folders ({count} locations)\n{folders}",
    "destination_more": "... and {count} more (hover to see all)",
    "destination_tooltip": "Source: {source}\nSave audio to: {folder}",
    "wav_tooltip": "WAV uses uncompressed PCM audio; bitrate does not apply.",
    "video_dialog": "Select Video Files",
    "video_filter": "Video Files (*.mp4 *.avi *.mov *.mkv *.webm *.m4v)",
    "folder_dialog": "Choose a common audio output folder (optional)",
    "ready": "Ready to convert",
    "convert": "Convert",
    "cancel": "Cancel",
    "starting": "Starting conversion...",
    "progress": "{name}: {current}% (batch: {overall}%)",
    "cancelling": "Cancelling conversion...",
    "cancelled_one": "Cancelled. {completed} file completed.",
    "cancelled_many": "Cancelled. {completed} files completed.",
    "partial": "Finished: {completed} succeeded, {failed} failed.",
    "more_errors": "...and {count} more.",
    "complete_one": "Complete: {completed} file converted.",
    "complete_many": "Complete: {completed} files converted.",
    "missing_selection_title": "Missing selection",
    "missing_selection": "Select at least one video.",
    "missing_folder_title": "Missing folder",
    "missing_folder": "The output folder no longer exists.",
    "cancelled_title": "Cancelled",
    "results_title": "Conversion results",
    "complete_title": "Complete",
    "error_audio": "No audio stream found:",
    "error_missing_file": "File not found:",
    "error_existing": "Output file already exists:",
    "error_output_folder": "Output folder does not exist:",
    "error_ffmpeg": "FFmpeg is unavailable:",
    "error_inspect": "Cannot inspect video:",
    "error_start": "Cannot start FFmpeg:",
    "error_failed": "FFmpeg failed:",
    "error_unsupported_format": "Unsupported output format:",
    "error_unsupported_bitrate": "Unsupported bitrate:",
    "error_timeout": "FFmpeg did not stop in time.",
    "error_unexpected": "Unexpected error:",
}

PT_BR = {
    "window_title": "Conversor de Vídeo para Áudio",
    "language_label": "Idioma:",
    "language_auto": "Automático (Windows)",
    "language_en": "English",
    "language_pt": "Português (Brasil)",
    "videos_label": "Vídeos para converter",
    "select_videos": "Selecionar vídeos",
    "remove_selected": "Remover selecionados",
    "clear_list": "Limpar lista",
    "output_format": "Formato de saída:",
    "bitrate": "Taxa de bits:",
    "choose_folder": "Escolher pasta de destino (opcional)",
    "source_folders": "Usar pastas de origem",
    "mixed_folders_hint": (
        "Os vídeos estão em pastas diferentes. Se preferir reunir todos os áudios, "
        "escolha uma pasta de destino. Isso é opcional."
    ),
    "destination_custom": "Salvar áudio em: {folder} (pasta escolhida)",
    "destination_none": "Salvar áudio em: pasta original de cada vídeo (automático)",
    "destination_single": "Salvar áudio em: {folder} (mesma pasta dos vídeos)",
    "destination_multiple": "Salvar áudio em: pastas originais ({count} locais)\n{folders}",
    "destination_more": "... e mais {count} (passe o mouse para ver todos)",
    "destination_tooltip": "Origem: {source}\nSalvar áudio em: {folder}",
    "wav_tooltip": "WAV usa áudio PCM sem compressão; a taxa de bits não se aplica.",
    "video_dialog": "Selecionar arquivos de vídeo",
    "video_filter": "Arquivos de vídeo (*.mp4 *.avi *.mov *.mkv *.webm *.m4v)",
    "folder_dialog": "Escolher uma pasta comum para os áudios (opcional)",
    "ready": "Pronto para converter",
    "convert": "Converter",
    "cancel": "Cancelar",
    "starting": "Iniciando conversão...",
    "progress": "{name}: {current}% (lote: {overall}%)",
    "cancelling": "Cancelando conversão...",
    "cancelled_one": "Cancelado. {completed} arquivo concluído.",
    "cancelled_many": "Cancelado. {completed} arquivos concluídos.",
    "partial": "Conversão finalizada. Sucessos: {completed}. Falhas: {failed}.",
    "more_errors": "... e mais {count} outras ocorrências.",
    "complete_one": "Concluído: {completed} arquivo convertido.",
    "complete_many": "Concluído: {completed} arquivos convertidos.",
    "missing_selection_title": "Nenhum vídeo selecionado",
    "missing_selection": "Selecione pelo menos um vídeo.",
    "missing_folder_title": "Pasta não encontrada",
    "missing_folder": "A pasta de destino não existe mais.",
    "cancelled_title": "Cancelado",
    "results_title": "Resultado da conversão",
    "complete_title": "Concluído",
    "error_audio": "Nenhuma faixa de áudio encontrada:",
    "error_missing_file": "Arquivo não encontrado:",
    "error_existing": "O arquivo de destino já existe:",
    "error_output_folder": "A pasta de destino não existe:",
    "error_ffmpeg": "FFmpeg indisponível:",
    "error_inspect": "Não foi possível analisar o vídeo:",
    "error_start": "Não foi possível iniciar o FFmpeg:",
    "error_failed": "Falha no FFmpeg:",
    "error_unsupported_format": "Formato de saída incompatível:",
    "error_unsupported_bitrate": "Taxa de bits não permitida:",
    "error_timeout": "O FFmpeg não foi encerrado a tempo.",
    "error_unexpected": "Erro inesperado:",
}

CATALOGS = {"en": EN, "pt_BR": PT_BR}

ERROR_KEYS = (
    "error_audio", "error_missing_file", "error_existing",
    "error_output_folder", "error_ffmpeg", "error_inspect", "error_start",
    "error_failed", "error_unsupported_format", "error_unsupported_bitrate",
    "error_timeout", "error_unexpected",
)


def effective_language(choice: str, system_locale: str | None = None) -> str:
    """Follow Windows locale on Auto; recognize regional variants of Portuguese."""
    if choice in CATALOGS:
        return choice
    locale = (system_locale or QLocale.system().name()).lower()
    return "pt_BR" if locale == "pt" or locale.startswith("pt_") else "en"


def translate(lang: str, key: str, **values: object) -> str:
    if key in ("complete", "cancelled"):
        key = key + ("_one" if values.get("completed") == 1 else "_many")
    catalog = CATALOGS.get(lang, EN)
    template = catalog.get(key, EN.get(key, key))
    return template.format(**values)


def translate_failure(lang: str, message: str) -> str:
    """Translate known application error prefixes; keep FFmpeg diagnostics intact."""
    for key in ERROR_KEYS:
        english = EN[key]
        if message.startswith(english):
            return translate(lang, key) + message[len(english):]
    return message
