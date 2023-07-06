from ui import MainWindow, setup_application

if __name__ == '__main__':
    app = setup_application()

    mainWin = MainWindow()
    mainWin.show()

    app.exec()