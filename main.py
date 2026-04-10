from data.db import init_db
from services.service_container import build_service_container
from ui.app import App


if __name__ == "__main__":
    init_db()
    app = App(build_service_container())
    app.mainloop()
