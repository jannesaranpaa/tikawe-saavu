import os
import re

csrf_field = (
    '\n    <input type="hidden" name="csrf_token" value="{{ session.csrf_token }}">'
)

for root, _, files in os.walk("templates"):
    for file in files:
        if file.endswith(".html"):
            path = os.path.join(root, file)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            # Inject the token only if it hasn"t been added yet
            if 'name="csrf_token"' not in content:
                # Find <form ... method="POST" ...> and append the hidden input
                new_content = re.sub(
                    r"(<form[^>]*method=[\"\']?(?:POST|post)[\"\']?[^>]*>)",
                    r"\1" + csrf_field,
                    content,
                )

                if new_content != content:
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(new_content)

print("✅ CSRF tokens successfully injected into all POST forms!")
