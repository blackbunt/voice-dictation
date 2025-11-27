#!/bin/bash
# Build script for Voice Dictation Arch package

set -e

echo "📦 Voice Dictation - Package Builder"
echo "===================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "PKGBUILD" ]; then
    echo -e "${RED}❌ Error: PKGBUILD not found. Run this script from the project root.${NC}"
    exit 1
fi

# Clean old packages
echo -e "${BLUE}🧹 Cleaning old packages...${NC}"
rm -f voice-dictation-*.pkg.tar.zst

# Build package
echo -e "${BLUE}🔨 Building package...${NC}"
makepkg -sf

# Find the built package
PKG_FILE=$(ls -t voice-dictation-*.pkg.tar.zst 2>/dev/null | head -n1)

if [ -z "$PKG_FILE" ]; then
    echo -e "${RED}❌ Error: Package build failed${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}✅ Package built successfully: $PKG_FILE${NC}"
echo ""

# Ask to install
read -p "❓ Install package now? [Y/n]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
    echo -e "${BLUE}📦 Installing package...${NC}"
    sudo pacman -U "$PKG_FILE"
    
    echo ""
    echo -e "${GREEN}✅ Installation complete!${NC}"
    echo ""
    echo "📝 Next steps:"
    echo "   1. Install whisper.cpp: ./bin/install-whisper.sh"
    echo "   2. Configure settings: voice-dictation-settings"
    echo "   3. Start dictation: voice-dictation"
    echo ""
    echo "⌨️  Default hotkey: Ctrl+Shift+Space"
else
    echo ""
    echo "ℹ️  Package ready for installation:"
    echo "   sudo pacman -U $PKG_FILE"
fi

echo ""
echo "📄 Package info:"
pacman -Qip "$PKG_FILE" 2>/dev/null || true
