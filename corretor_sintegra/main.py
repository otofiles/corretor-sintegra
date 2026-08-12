from __future__ import annotations

import sys
from pathlib import Path

from core.caminhos import esta_empacotado, pasta_embutida


def main(raiz: Path | None = None) -> int:
    if raiz is None:
        raiz = pasta_embutida()
    raiz = Path(raiz)
    if str(raiz) not in sys.path:
        sys.path.insert(0, str(raiz))

    from ui.app import Aplicacao

    app = Aplicacao(raiz)
    app.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
