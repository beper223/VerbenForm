# python manage.py import_verbs verbs.sample.json
# читает verb_type
# валидирует по VerbType из src.common.choices
# применяет по правилам:
# без --force: ставит только если verb.verb_type пустой (и в --debug пишет SKIP ...)
# с --force: перезаписывает

import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from src.common.choices import AuxiliaryVerb, GermanCase, Pronoun, Reflexiv, Tense, VerbType, LanguageCode, CEFRLevel
from src.personal_forms.models import Verb, VerbForm, VerbTranslation


class Command(BaseCommand):
    help = "Import verbs and their forms (Präsens/Präteritum) from a JSON file."

    def add_arguments(self, parser):
        parser.add_argument(
            "json_path",
            type=str,
            help="Path to JSON file with verbs.",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Overwrite existing values/forms.",
        )
        parser.add_argument(
            "--debug",
            action="store_true",
            help="Log skipped updates due to already filled values.",
        )

    def handle(self, *args, **options):
        json_path = Path(options["json_path"])
        force: bool = options["force"]
        debug: bool = options["debug"]

        if not json_path.exists():
            raise CommandError(f"JSON file not found: {json_path}")
        if not json_path.is_file():
            raise CommandError(f"Not a file: {json_path}")

        try:
            payload = json.loads(json_path.read_text(encoding="utf-8"))
        except Exception as exc:
            raise CommandError(f"Failed to read/parse JSON: {exc}")

        verbs = payload.get("verbs")
        if not isinstance(verbs, list):
            raise CommandError("Invalid JSON: top-level key 'verbs' must be a list")

        allowed_pronouns = set(Pronoun.get_available_values())
        allowed_tenses = {Tense.PRAESENS.value, Tense.PRAETERITUM.value}
        allowed_aux = {a.value for a in AuxiliaryVerb}
        allowed_verb_types = {t.value for t in VerbType}
        allowed_language_codes = set(LanguageCode.get_available_values())
        allowed_reflexivitaet = {r.value for r in Reflexiv}
        allowed_cases = {
            GermanCase.AKK.name,
            GermanCase.DAT.name,
            GermanCase.AKK.value,
            GermanCase.DAT.value,
        }
        allowed_levels = {l.value for l in CEFRLevel}

        created_verbs = 0
        updated_verbs = 0
        created_forms = 0
        updated_forms = 0
        created_translations = 0
        updated_translations = 0
        skipped = 0

        for idx, item in enumerate(verbs, start=1):
            if not isinstance(item, dict):
                raise CommandError(f"Invalid verb entry at index {idx}: expected object")

            infinitive = (item.get("infinitive") or "").strip()
            if not infinitive:
                raise CommandError(f"Invalid verb entry at index {idx}: missing 'infinitive'")

            with transaction.atomic():
                verb, verb_created = Verb.objects.get_or_create(
                    infinitive=infinitive,
                    defaults={
                        "verb_type": VerbType.REGULAR.value,
                        "level": CEFRLevel.A1.value,
                    },
                )
                if verb_created:
                    created_verbs += 1

                verb_changed = False

                verb_type = item.get("verb_type")
                if verb_type is not None:
                    verb_type = str(verb_type).strip()
                    if verb_type and verb_type not in allowed_verb_types:
                        raise CommandError(
                            f"Invalid verb_type '{verb_type}' for verb '{infinitive}'. "
                            f"Allowed: {sorted(allowed_verb_types)}"
                        )
                    if force or not verb.verb_type:
                        if verb_type and verb_type != verb.verb_type:
                            verb.verb_type = verb_type
                            verb_changed = True
                    else:
                        skipped += 1
                        if debug:
                            self.stdout.write(
                                f"SKIP verb.verb_type for '{infinitive}': already set ({verb.verb_type})"
                            )

                level = item.get("level")
                if level is not None:
                    level = str(level).strip()
                    if level and level not in allowed_levels:
                        raise CommandError(
                            f"Invalid level '{level}' for verb '{infinitive}'. "
                            f"Allowed: {sorted(allowed_levels)}"
                        )
                    if force or not verb.level:
                        if level and level != verb.level:
                            verb.level = level
                            verb_changed = True
                    else:
                        skipped += 1
                        if debug:
                            self.stdout.write(
                                f"SKIP verb.level for '{infinitive}': already set ({verb.level})"
                            )

                is_trennbare = item.get("is_trennbare")
                if is_trennbare is not None:
                    if isinstance(is_trennbare, bool):
                        parsed_is_trennbare = is_trennbare
                    elif isinstance(is_trennbare, (int, float)):
                        parsed_is_trennbare = bool(is_trennbare)
                    else:
                        parsed_is_trennbare_str = str(is_trennbare).strip().lower()
                        if parsed_is_trennbare_str in {"true", "1", "yes", "y", "on"}:
                            parsed_is_trennbare = True
                        elif parsed_is_trennbare_str in {"false", "0", "no", "n", "off"}:
                            parsed_is_trennbare = False
                        else:
                            raise CommandError(
                                f"Invalid is_trennbare '{is_trennbare}' for verb '{infinitive}'. "
                                "Expected boolean."
                            )

                    if force or verb_created or (not verb.is_trennbare and parsed_is_trennbare):
                        if parsed_is_trennbare != verb.is_trennbare:
                            verb.is_trennbare = parsed_is_trennbare
                            verb_changed = True
                    else:
                        skipped += 1
                        if debug:
                            self.stdout.write(
                                f"SKIP verb.is_trennbare for '{infinitive}': already set ({verb.is_trennbare})"
                            )

                reflexivitaet = item.get("reflexivitaet")
                if reflexivitaet is not None:
                    reflexivitaet = str(reflexivitaet).strip()
                    if reflexivitaet and reflexivitaet not in allowed_reflexivitaet:
                        raise CommandError(
                            f"Invalid reflexivitaet '{reflexivitaet}' for verb '{infinitive}'. "
                            f"Allowed: {sorted(allowed_reflexivitaet)}"
                        )

                    default_reflexivitaet = Reflexiv.NREFL.value
                    if force or verb_created or verb.reflexivitaet == default_reflexivitaet:
                        if reflexivitaet and reflexivitaet != verb.reflexivitaet:
                            verb.reflexivitaet = reflexivitaet
                            verb_changed = True
                    else:
                        skipped += 1
                        if debug:
                            self.stdout.write(
                                f"SKIP verb.reflexivitaet for '{infinitive}': already set ({verb.reflexivitaet})"
                            )

                case = item.get("case")
                if case is not None:
                    case = str(case).strip()
                    if case and case not in allowed_cases:
                        raise CommandError(
                            f"Invalid case '{case}' for verb '{infinitive}'. "
                            f"Allowed: {sorted(allowed_cases)}"
                        )

                    normalized_case = case
                    if case == GermanCase.AKK.value:
                        normalized_case = GermanCase.AKK.name
                    elif case == GermanCase.DAT.value:
                        normalized_case = GermanCase.DAT.name

                    if force or not verb.case:
                        if normalized_case != (verb.case or ""):
                            verb.case = normalized_case or None
                            verb_changed = True
                    else:
                        skipped += 1
                        if debug:
                            self.stdout.write(
                                f"SKIP verb.case for '{infinitive}': already set ({verb.case})"
                            )

                perfekt = item.get("perfekt") or {}
                if not isinstance(perfekt, dict):
                    raise CommandError(
                        f"Invalid verb entry '{infinitive}': 'perfekt' must be an object"
                    )

                auxiliary = perfekt.get("auxiliary")
                if auxiliary is not None:
                    auxiliary = str(auxiliary).strip()
                    if auxiliary and auxiliary not in allowed_aux:
                        raise CommandError(
                            f"Invalid auxiliary '{auxiliary}' for verb '{infinitive}'. "
                            f"Allowed: {sorted(allowed_aux)}"
                        )
                    if force or not verb.auxiliary:
                        if auxiliary != verb.auxiliary:
                            verb.auxiliary = auxiliary or None
                            verb_changed = True
                    else:
                        skipped += 1
                        if debug:
                            self.stdout.write(
                                f"SKIP verb.auxiliary for '{infinitive}': already set ({verb.auxiliary})"
                            )

                participle_ii = perfekt.get("participle_ii")
                if participle_ii is not None:
                    participle_ii = str(participle_ii).strip()
                    if force or not verb.participle_ii:
                        if participle_ii != (verb.participle_ii or ""):
                            verb.participle_ii = participle_ii or None
                            verb_changed = True
                    else:
                        skipped += 1
                        if debug:
                            self.stdout.write(
                                f"SKIP verb.participle_ii for '{infinitive}': already set ({verb.participle_ii})"
                            )

                forms = item.get("forms") or {}
                if not isinstance(forms, dict):
                    raise CommandError(
                        f"Invalid verb entry '{infinitive}': 'forms' must be an object"
                    )

                for tense_name, pronoun_map in forms.items():
                    if tense_name not in allowed_tenses:
                        raise CommandError(
                            f"Invalid tense '{tense_name}' for verb '{infinitive}'. "
                            f"Allowed: {sorted(allowed_tenses)}"
                        )
                    if not isinstance(pronoun_map, dict):
                        raise CommandError(
                            f"Invalid forms for verb '{infinitive}', tense '{tense_name}': must be an object"
                        )

                    for pronoun_value, form_value in pronoun_map.items():
                        pronoun_value = str(pronoun_value).strip()
                        if pronoun_value not in allowed_pronouns:
                            raise CommandError(
                                f"Invalid pronoun '{pronoun_value}' for verb '{infinitive}', tense '{tense_name}'. "
                                f"Allowed: {sorted(allowed_pronouns)}"
                            )

                        form_value = "" if form_value is None else str(form_value).strip()
                        if not form_value:
                            raise CommandError(
                                f"Empty form for verb '{infinitive}', tense '{tense_name}', pronoun '{pronoun_value}'"
                            )

                        vf, vf_created = VerbForm.objects.get_or_create(
                            verb=verb,
                            tense=tense_name,
                            pronoun=pronoun_value,
                            defaults={"form": form_value},
                        )

                        if vf_created:
                            created_forms += 1
                            continue

                        if force:
                            if vf.form != form_value:
                                vf.form = form_value
                                vf.save(update_fields=["form"])
                                updated_forms += 1
                            continue

                        if not vf.form:
                            vf.form = form_value
                            vf.save(update_fields=["form"])
                            updated_forms += 1
                        else:
                            skipped += 1
                            if debug:
                                self.stdout.write(
                                    f"SKIP VerbForm for '{infinitive}' ({tense_name}, {pronoun_value}): already set ({vf.form})"
                                )

                translations = item.get("translations")
                if translations is not None:
                    if not isinstance(translations, dict):
                        raise CommandError(
                            f"Invalid verb entry '{infinitive}': 'translations' must be an object (language_code -> translation)"
                        )

                    for language_code, translation_value in translations.items():
                        language_code = str(language_code).strip()
                        if not language_code:
                            raise CommandError(
                                f"Invalid translation language_code for verb '{infinitive}': empty"
                            )
                        if language_code not in allowed_language_codes:
                            raise CommandError(
                                f"Invalid translation language_code '{language_code}' for verb '{infinitive}'. "
                                f"Allowed: {sorted(allowed_language_codes)}"
                            )
                        translation_value = "" if translation_value is None else str(translation_value).strip()
                        if not translation_value:
                            raise CommandError(
                                f"Empty translation for verb '{infinitive}', language '{language_code}'"
                            )

                        vt, vt_created = VerbTranslation.objects.get_or_create(
                            verb=verb,
                            language_code=language_code,
                            defaults={"translation": translation_value},
                        )
                        if vt_created:
                            created_translations += 1
                            continue

                        if force:
                            if vt.translation != translation_value:
                                vt.translation = translation_value
                                vt.save(update_fields=["translation"])
                                updated_translations += 1
                            continue

                        if not vt.translation:
                            vt.translation = translation_value
                            vt.save(update_fields=["translation"])
                            updated_translations += 1
                        else:
                            skipped += 1
                            if debug:
                                self.stdout.write(
                                    f"SKIP VerbTranslation for '{infinitive}' ({language_code}): already set ({vt.translation})"
                                )

                if verb_changed:
                    verb.save()
                    updated_verbs += 1

        self.stdout.write(
            "\n".join(
                [
                    f"Imported from: {json_path}",
                    f"Verbs: created={created_verbs}, updated={updated_verbs}",
                    f"Forms: created={created_forms}, updated={updated_forms}",
                    f"Translations: created={created_translations}, updated={updated_translations}",
                    f"Skipped={skipped} (use --debug for details)",
                ]
            )
        )
