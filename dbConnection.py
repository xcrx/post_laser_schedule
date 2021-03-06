"""
Use this is create connections with databases.
"""
from PyQt4 import QtGui, QtSql, QtCore, uic
from functions import get_users
from query import query


def default_connection():
    """
    Creates a new connection using the default connection name.
    'reader' user should only have Select permissions
    Returns false if the connection couldn't be made.
    """
    
    QtSql.QSqlDatabase.database('qt_sql_default_connection').close()
    QtSql.QSqlDatabase.removeDatabase('qt_sql_default_connection')
    db = QtSql.QSqlDatabase.addDatabase("QMYSQL")
    host, database = read_settings("default")
    db.setUserName('reader')
    db.setHostName(host)
    db.setDatabaseName(database)
    if db.open():
        return True
    else:
        db_err(db)
        return False


def new_connection(name, host=None, database=None):
    """
    Returns a new connection named 'name'. 'user' and 'password'
    must be supplied. Use this function to create a privileged 
    connection or to connect to a different server.
    
    If a connection named %name already exists it returns that
    connection instead of making a new connection.
    
    Returns an empty connection and False if the new connection 
    could not be made.
    """
    if QtSql.QSqlDatabase.database(name).open():
        db = QtSql.QSqlDatabase.database(name)
        return db, True
    else:
        if host == None or database == None:
            host, database = read_settings(name)
        login_dialog = LoginDialog()
        login = login_dialog.get_data(host)
        if not login:
            return None, False
        db = QtSql.QSqlDatabase.addDatabase("QMYSQL", name)
        db.setUserName(login[0])
        db.setHostName(host)
        db.setDatabaseName(database)
        db.setPassword(login[1])
        if db.open():
            return db, True
        else:
            db_err(db)
            return None, False


def close_connection(name):
    """
    Close and remove the connection 'name' if it is open.
    """
    if QtSql.QSqlDatabase.database(name).open():
        QtSql.QSqlDatabase.database(name).close()
    QtSql.QSqlDatabase.removeDatabase(name)
    print "Connection closed. New connection required"


def close_all_connections():
    """
    Loops all connections, closes and removes them.
    """
    for name in QtSql.QSqlDatabase.connectionNames():
        if QtSql.QSqlDatabase.database(name).open():
            QtSql.QSqlDatabase.database(name).close()
        QtSql.QSqlDatabase.removeDatabase(name)


def db_err(qry):
    """
    This error is used extensively.
    """
    if qry is None:
        QtGui.QMessageBox.critical(None, "Database Error", "An unknown error occurred")
    else:
        QtGui.QMessageBox.critical(None, "Database Error", qry.lastError().text())
    return


def start_transaction(db='qt_sql_default_connection'):
    db = QtSql.QSqlDatabase.database(db)
    if db.transaction():
        return True
    else:
        print db.lastError().text()
        QtGui.QMessageBox.critical(None, "Transaction Error", "Could not start the transaction.")
        return False


def commit_transaction(db='qt_sql_default_connection'):
    db = QtSql.QSqlDatabase.database(db)
    if db.commit():
        return True
    else:
        QtGui.QMessageBox.critical(None, "Transaction Error", "Could not commit the transaction.")
        return False


def rollback_transaction(db='qt_sql_default_connection'):
    db = QtSql.QSqlDatabase.database(db)
    return db.rollback()

####Settings Block
#Reads and saves database settings across sessions.


def write_settings(host, database, group):
    settings = QtCore.QSettings("Doyle Mfg", "Post Laser Schedule")
    settings.setDefaultFormat(1)
    settings.beginGroup(group)
    settings.setValue('host', QtCore.QString(host))
    settings.setValue('database', QtCore.QString(database))
    settings.endGroup()


def read_settings(group):
    settings = QtCore.QSettings("Doyle Mfg", "Post Laser Schedule")
    settings.setDefaultFormat(1)
    settings.beginGroup(group)
    host = settings.value('host', '192.168.1.39').toString()
    database = settings.value('database', 'inventorysystem').toString()
    write_settings(host, database, group)
    return host, database


class LoginDialog(QtGui.QDialog):

    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.username = QtGui.QLineEdit()
        self.password = QtGui.QLineEdit()
        self.password.setEchoMode(QtGui.QLineEdit.Password)
        username_label = QtGui.QLabel("Username")
        password_label = QtGui.QLabel("Password")
        self.cancel_button = QtGui.QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        self.login_button = QtGui.QPushButton("Login")
        self.login_button.clicked.connect(self.accept)
        self.login_button.setDefault(True)

        layout = QtGui.QGridLayout()
        layout.addWidget(username_label, 0, 0)
        layout.addWidget(self.username, 0, 1, 1, 2)
        layout.addWidget(password_label, 1, 0)
        layout.addWidget(self.password, 1, 1, 1, 2)
        layout.addWidget(self.cancel_button, 2, 1)
        layout.addWidget(self.login_button, 2, 2)
        self.setLayout(layout)
        self.username.setFocus()

    def get_data(self, host):
        self.setWindowTitle("%s Login" % host)
        ok = self.exec_()
        username = self.username.text()
        password = self.password.text()
        if ok:
            if username != "" and password != "":
                return [username, password]
            else:
                self.get_data(host)
        else:
            return False