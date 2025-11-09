"""
Tests for DatabaseManager class

This module tests the database manager functionality including:
- Initialization and configuration
- Connection string creation
- Query execution
- Error handling
"""
import pytest
from unittest.mock import Mock, MagicMock, patch, call
import pyodbc


@pytest.fixture
def mock_connection_config():
    """Mock ConnectionConfig class"""
    with patch('src.database.database_manager.ConnectionConfig') as mock:
        config_instance = MagicMock()
        config_instance.get_connection_string.return_value = "mock_connection_string"
        config_instance.get_current_user.return_value = "test_user"
        config_instance.get_config.return_value = {
            "server": "test-server",
            "database": "test-db"
        }
        mock.return_value = config_instance
        yield mock


@pytest.mark.unit
@pytest.mark.database
class TestDatabaseManagerInitialization:
    """Test DatabaseManager initialization"""

    def test_init_without_connection_info(self, mock_connection_config):
        """Test initialization without connection info (using config file)"""
        from src.database.database_manager import DatabaseManager

        db = DatabaseManager()

        assert db.connection_string == "mock_connection_string"
        assert db.current_user == "test_user"
        mock_connection_config.assert_called_once()

    def test_init_with_connection_info(self, mock_connection_config):
        """Test initialization with connection info from login"""
        from src.database.database_manager import DatabaseManager

        connection_info = {
            'config': {'server': 'custom-server', 'database': 'custom-db'},
            'connection_string': 'custom_connection_string',
            'current_user': 'custom_user'
        }

        db = DatabaseManager(connection_info)

        assert db.connection_string == 'custom_connection_string'
        assert db.current_user == 'custom_user'
        assert db.config_manager.config == connection_info['config']


@pytest.mark.unit
@pytest.mark.database
class TestDatabaseManagerConnection:
    """Test database connection functionality"""

    @patch('src.database.database_manager.pyodbc.connect')
    def test_connection_successful(self, mock_connect, mock_connection_config):
        """Test successful database connection"""
        from src.database.database_manager import DatabaseManager

        mock_conn = MagicMock()
        mock_connect.return_value.__enter__.return_value = mock_conn

        db = DatabaseManager()
        result = db.test_connection()

        assert result is True
        mock_connect.assert_called_once_with(db.connection_string)

    @patch('src.database.database_manager.pyodbc.connect')
    @patch('tkinter.messagebox.showerror')
    def test_connection_failure(self, mock_messagebox, mock_connect, mock_connection_config):
        """Test database connection failure"""
        from src.database.database_manager import DatabaseManager

        mock_connect.side_effect = Exception("Connection failed")

        db = DatabaseManager()
        result = db.test_connection()

        assert result is False
        mock_messagebox.assert_called_once()


@pytest.mark.unit
@pytest.mark.database
class TestDatabaseManagerQueries:
    """Test database query execution"""

    @patch('src.database.database_manager.pyodbc.connect')
    def test_execute_query_success(self, mock_connect, mock_connection_config):
        """Test successful query execution"""
        from src.database.database_manager import DatabaseManager

        # Setup mock cursor with results
        mock_cursor = MagicMock()
        mock_cursor.description = [('id',), ('name',)]
        mock_cursor.fetchall.return_value = [
            (1, 'Test1'),
            (2, 'Test2')
        ]

        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value.__enter__.return_value = mock_conn

        db = DatabaseManager()
        results = db.execute_query("SELECT * FROM test", ())

        assert len(results) == 2
        assert results[0] == {'id': 1, 'name': 'Test1'}
        assert results[1] == {'id': 2, 'name': 'Test2'}
        mock_cursor.execute.assert_called_once_with("SELECT * FROM test", ())

    @patch('src.database.database_manager.pyodbc.connect')
    def test_execute_query_with_params(self, mock_connect, mock_connection_config):
        """Test query execution with parameters"""
        from src.database.database_manager import DatabaseManager

        mock_cursor = MagicMock()
        mock_cursor.description = [('count',)]
        mock_cursor.fetchall.return_value = [(5,)]

        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value.__enter__.return_value = mock_conn

        db = DatabaseManager()
        results = db.execute_query("SELECT COUNT(*) as count FROM test WHERE id = ?", (1,))

        assert results[0]['count'] == 5
        mock_cursor.execute.assert_called_once_with(
            "SELECT COUNT(*) as count FROM test WHERE id = ?",
            (1,)
        )

    @patch('src.database.database_manager.pyodbc.connect')
    @patch('tkinter.messagebox.showerror')
    def test_execute_query_error(self, mock_messagebox, mock_connect, mock_connection_config):
        """Test query execution error handling"""
        from src.database.database_manager import DatabaseManager

        mock_connect.side_effect = Exception("Query error")

        db = DatabaseManager()
        results = db.execute_query("SELECT * FROM test")

        assert results == []
        mock_messagebox.assert_called_once()


@pytest.mark.unit
@pytest.mark.database
class TestDatabaseManagerNonQuery:
    """Test non-query execution (INSERT, UPDATE, DELETE)"""

    @patch('src.database.database_manager.pyodbc.connect')
    def test_execute_non_query_success(self, mock_connect, mock_connection_config):
        """Test successful non-query execution"""
        from src.database.database_manager import DatabaseManager

        mock_cursor = MagicMock()
        mock_cursor.rowcount = 3

        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value.__enter__.return_value = mock_conn

        db = DatabaseManager()
        rowcount = db.execute_non_query("INSERT INTO test VALUES (?, ?)", (1, 'test'))

        assert rowcount == 3
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()

    @patch('src.database.database_manager.pyodbc.connect')
    @patch('tkinter.messagebox.showerror')
    def test_execute_non_query_error(self, mock_messagebox, mock_connect, mock_connection_config):
        """Test non-query execution error handling"""
        from src.database.database_manager import DatabaseManager

        mock_connect.side_effect = Exception("Insert error")

        db = DatabaseManager()
        rowcount = db.execute_non_query("INSERT INTO test VALUES (?, ?)", (1, 'test'))

        assert rowcount == 0
        mock_messagebox.assert_called_once()


@pytest.mark.unit
@pytest.mark.database
class TestDatabaseManagerStoredProcedure:
    """Test stored procedure execution"""

    @patch('src.database.database_manager.pyodbc.connect')
    def test_execute_sp_success(self, mock_connect, mock_connection_config):
        """Test successful stored procedure execution"""
        from src.database.database_manager import DatabaseManager

        mock_cursor = MagicMock()
        mock_cursor.description = [('result',)]
        mock_cursor.fetchall.return_value = [('success',)]

        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value.__enter__.return_value = mock_conn

        db = DatabaseManager()
        results = db.execute_sp("sp_test", (1, 'param'))

        assert len(results) == 1
        assert results[0]['result'] == 'success'
        mock_cursor.execute.assert_called_once()

    @patch('src.database.database_manager.pyodbc.connect')
    @patch('tkinter.messagebox.showerror')
    def test_execute_sp_error(self, mock_messagebox, mock_connect, mock_connection_config):
        """Test stored procedure error handling"""
        from src.database.database_manager import DatabaseManager

        mock_connect.side_effect = Exception("SP error")

        db = DatabaseManager()
        results = db.execute_sp("sp_test", (1,))

        assert results == []
        mock_messagebox.assert_called_once()


@pytest.mark.unit
@pytest.mark.database
class TestDatabaseManagerConfiguration:
    """Test configuration management"""

    def test_get_connection_info(self, mock_connection_config):
        """Test getting connection information"""
        from src.database.database_manager import DatabaseManager

        db = DatabaseManager()
        info = db.get_connection_info()

        assert 'config' in info
        assert 'connection_string' in info
        assert 'current_user' in info
        assert info['connection_string'] == "mock_connection_string"
        assert info['current_user'] == "test_user"

    def test_update_connection_success(self, mock_connection_config):
        """Test successful connection update"""
        from src.database.database_manager import DatabaseManager

        db = DatabaseManager()
        db.config_manager.update_config.return_value = True
        db.config_manager.get_connection_string.return_value = "new_connection_string"
        db.config_manager.get_current_user.return_value = "new_user"

        new_config = {'server': 'new-server', 'database': 'new-db'}
        result = db.update_connection(new_config)

        assert result is True
        assert db.connection_string == "new_connection_string"
        assert db.current_user == "new_user"

    @patch('tkinter.messagebox.showerror')
    def test_update_connection_failure(self, mock_messagebox, mock_connection_config):
        """Test connection update failure"""
        from src.database.database_manager import DatabaseManager

        db = DatabaseManager()
        db.config_manager.update_config.side_effect = Exception("Update error")

        new_config = {'server': 'new-server'}
        result = db.update_connection(new_config)

        assert result is False
        mock_messagebox.assert_called_once()
