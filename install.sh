#!/bin/bash
# ApexAurum Installation Script
# Works on Linux, macOS, and WSL
#
# Usage: ./install.sh [--with-sandbox]
#
# Options:
#   --with-sandbox    Also build the Docker sandbox for code execution

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
info() { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[OK]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# Header
echo ""
echo -e "${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${NC}           ${GREEN}ApexAurum Installation Script${NC}                  ${BLUE}║${NC}"
echo -e "${BLUE}║${NC}     Production-grade AI Chat Interface for Claude        ${BLUE}║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Parse arguments
WITH_SANDBOX=false
for arg in "$@"; do
    case $arg in
        --with-sandbox)
            WITH_SANDBOX=true
            shift
            ;;
        --help|-h)
            echo "Usage: ./install.sh [--with-sandbox]"
            echo ""
            echo "Options:"
            echo "  --with-sandbox    Also build the Docker sandbox for code execution"
            echo "  --help, -h        Show this help message"
            exit 0
            ;;
    esac
done

# Check we're in the right directory
if [ ! -f "main.py" ] || [ ! -f "requirements.txt" ]; then
    error "Please run this script from the ApexAurum project root directory"
fi

# ============================================================================
# Step 1: Check Python version
# ============================================================================
info "Checking Python version..."

# Try python3 first, then python
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    error "Python not found. Please install Python 3.10 or higher."
fi

# Check version
PYTHON_VERSION=$($PYTHON_CMD -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PYTHON_MAJOR=$($PYTHON_CMD -c 'import sys; print(sys.version_info.major)')
PYTHON_MINOR=$($PYTHON_CMD -c 'import sys; print(sys.version_info.minor)')

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
    error "Python 3.10+ required. Found: $PYTHON_VERSION"
fi

success "Python $PYTHON_VERSION found"

# ============================================================================
# Step 2: Create virtual environment
# ============================================================================
info "Creating virtual environment..."

if [ -d "venv" ]; then
    warn "Virtual environment already exists. Skipping creation."
else
    $PYTHON_CMD -m venv venv
    success "Virtual environment created"
fi

# Activate venv
source venv/bin/activate
success "Virtual environment activated"

# ============================================================================
# Step 3: Upgrade pip
# ============================================================================
info "Upgrading pip..."
pip install --upgrade pip -q
success "pip upgraded"

# ============================================================================
# Step 4: Install dependencies
# ============================================================================
info "Installing dependencies (this may take a few minutes)..."
echo ""

# Install in stages for better feedback
pip install -q streamlit anthropic python-dotenv
success "Core dependencies installed"

pip install -q chromadb sentence-transformers
success "Vector/ML dependencies installed"

pip install -q -r requirements.txt
success "All dependencies installed"

echo ""

# ============================================================================
# Step 5: Set up environment file
# ============================================================================
info "Setting up environment configuration..."

if [ -f ".env" ]; then
    warn ".env file already exists. Skipping creation."
else
    cp .env.example .env
    success ".env file created from template"
    echo ""
    warn "IMPORTANT: Edit .env and add your ANTHROPIC_API_KEY"
    echo "  Get your key at: https://console.anthropic.com/"
fi

# ============================================================================
# Step 6: Create sandbox directory
# ============================================================================
info "Creating sandbox directory..."

mkdir -p sandbox
success "sandbox/ directory ready"

# ============================================================================
# Step 7: Optional Docker sandbox setup
# ============================================================================
if [ "$WITH_SANDBOX" = true ]; then
    echo ""
    info "Setting up Docker sandbox..."

    if ! command -v docker &> /dev/null; then
        warn "Docker not found. Skipping sandbox build."
        warn "Install Docker and run: docker build -t apex-sandbox:latest ."
    else
        if docker info &> /dev/null; then
            info "Building sandbox container (this may take several minutes)..."
            docker build -t apex-sandbox:latest .
            success "Docker sandbox built: apex-sandbox:latest"
        else
            warn "Docker daemon not accessible. You may need to:"
            echo "  1. Start Docker: sudo systemctl start docker"
            echo "  2. Add user to docker group: sudo usermod -aG docker \$USER"
            echo "  3. Log out and back in, then run: docker build -t apex-sandbox:latest ."
        fi
    fi
fi

# ============================================================================
# Step 8: Verify installation
# ============================================================================
echo ""
info "Verifying installation..."

TOOL_COUNT=$(python -c "from tools import ALL_TOOLS; print(len(ALL_TOOLS))" 2>/dev/null || echo "0")

if [ "$TOOL_COUNT" -gt 0 ]; then
    success "Installation verified: $TOOL_COUNT tools loaded"
else
    warn "Could not verify tool count. This may be OK - check after first run."
fi

# ============================================================================
# Done!
# ============================================================================
echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║${NC}              Installation Complete!                       ${GREEN}║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo ""
echo "  1. Edit your API key:"
echo "     ${YELLOW}nano .env${NC}  (or your preferred editor)"
echo "     Add: ANTHROPIC_API_KEY=sk-ant-your-key-here"
echo ""
echo "  2. Start the application:"
echo "     ${YELLOW}source venv/bin/activate${NC}"
echo "     ${YELLOW}streamlit run main.py${NC}"
echo ""
echo "  3. Open in browser:"
echo "     ${YELLOW}http://localhost:8501${NC}"
echo ""

if [ "$WITH_SANDBOX" = false ]; then
    echo -e "${BLUE}Optional:${NC} For Docker code execution sandbox:"
    echo "     ${YELLOW}./install.sh --with-sandbox${NC}"
    echo "     or: ${YELLOW}docker build -t apex-sandbox:latest .${NC}"
    echo ""
fi

echo -e "Documentation: ${YELLOW}README.md${NC}, ${YELLOW}START_HERE.md${NC}"
echo ""
