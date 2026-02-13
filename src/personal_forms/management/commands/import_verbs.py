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

from src.common.choices import AuxiliaryVerb, Pronoun, Tense, VerbType
from src.personal_forms.models import Verb, VerbForm


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

        created_verbs = 0
        updated_verbs = 0
        created_forms = 0
        updated_forms = 0
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
                    defaults={"verb_type": VerbType.REGULAR.value},
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

                if verb_changed:
                    verb.save()
                    updated_verbs += 1

        self.stdout.write(
            "\n".join(
                [
                    f"Imported from: {json_path}",
                    f"Verbs: created={created_verbs}, updated={updated_verbs}",
                    f"Forms: created={created_forms}, updated={updated_forms}",
                    f"Skipped={skipped} (use --debug for details)",
                ]
            )
        )
