#!/usr/bin/env bash
# Update CITATION.cff and .zenodo.json with real Zenodo DOI
# Usage: ./update_doi.sh ZENODO_DOI_NUMBER
# Example: ./update_doi.sh 13957842

set -euo pipefail

if [ $# -ne 1 ]; then
    echo "Usage: $0 <zenodo_doi_number>"
    echo "Example: $0 13957842"
    echo ""
    echo "Get your DOI from: https://zenodo.org/account/settings/github/"
    exit 1
fi

DOI_NUM=$1
FULL_DOI="10.5281/zenodo.${DOI_NUM}"

echo "Updating files with DOI: ${FULL_DOI}"

# Update CITATION.cff
sed -i "s/doi: \"10.5281\/zenodo.TBD\"/doi: \"${FULL_DOI}\"/" CITATION.cff
echo "✓ Updated CITATION.cff"

# Update .zenodo.json (if it contains the old DOI reference)
if grep -q "zenodo.TBD" .zenodo.json 2>/dev/null; then
    sed -i "s/zenodo.TBD/zenodo.${DOI_NUM}/g" .zenodo.json
    echo "✓ Updated .zenodo.json"
fi

# Update README.md if it has DOI placeholder
if grep -q "zenodo.TBD" README.md 2>/dev/null; then
    sed -i "s/zenodo.TBD/zenodo.${DOI_NUM}/g" README.md
    echo "✓ Updated README.md"
fi

# Update README_API.md if it has DOI placeholder
if grep -q "zenodo.TBD" README_API.md 2>/dev/null; then
    sed -i "s/zenodo.TBD/zenodo.${DOI_NUM}/g" README_API.md
    echo "✓ Updated README_API.md"
fi

# Update configs/uha_anchor.example.json
if grep -q "zenodo.TBD" configs/uha_anchor.example.json 2>/dev/null; then
    sed -i "s/zenodo.TBD/zenodo.${DOI_NUM}/g" configs/uha_anchor.example.json
    echo "✓ Updated configs/uha_anchor.example.json"
fi

echo ""
echo "All files updated with DOI: ${FULL_DOI}"
echo ""
echo "Next steps:"
echo "1. Verify changes: git diff"
echo "2. Commit: git add -A && git commit -m \"Update DOI to ${FULL_DOI}\""
echo "3. Push: git push"
echo "4. Add DOI badge to README.md:"
echo "   [![DOI](https://zenodo.org/badge/DOI/${FULL_DOI}.svg)](https://doi.org/${FULL_DOI})"
