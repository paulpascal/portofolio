{# Remove common accents so country/place labels collapse to a single canonical form. #}
{% macro strip_accents(col) %}
    initcap(
        translate(
            lower(trim({{ col }})),
            'àâäáãçèéêëìíîïñòóôöõùúûüýÿ',
            'aaaaaceeeeiiiinooooouuuuyy'
        )
    )
{% endmacro %}
