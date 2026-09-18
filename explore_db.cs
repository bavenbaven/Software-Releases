using System;
using System.Data;
using System.Reflection;
using System.IO;

class Program
{
    static void Main(string[] args)
    {
        string dbFile = args.Length > 0 ? args[0] : null;
        if (dbFile == null || !File.Exists(dbFile))
        {
            Console.WriteLine("Usage: explore_db.exe <backup_file.bak>");
            return;
        }

        try
        {
            string appDir = @"D:\简单客手机维修管理系统";
            Assembly sqlite = Assembly.LoadFrom(Path.Combine(appDir, "System.Data.SQLite.dll"));
            Type connType = sqlite.GetType("System.Data.SQLite.SQLiteConnection");
            string connString = "Data Source=" + dbFile + ";Password=538e6c48746f4d6;";
            object conn = Activator.CreateInstance(connType, new object[] { connString });
            connType.GetMethod("Open").Invoke(conn, null);

            Type cmdType = sqlite.GetType("System.Data.SQLite.SQLiteCommand");
            string sql = "SELECT name, sql FROM sqlite_master WHERE type='table' ORDER BY name;";
            object cmd = Activator.CreateInstance(cmdType, new object[] { sql, conn });

            using (IDataReader reader = (IDataReader)cmdType.GetMethod("ExecuteReader", new Type[0]).Invoke(cmd, null))
            {
                while (reader.Read())
                {
                    string tableName = reader[0].ToString();
                    string createSql = reader[1] == DBNull.Value ? "" : reader[1].ToString();
                    Console.WriteLine("=== TABLE: " + tableName + " ===");
                    Console.WriteLine(createSql);
                    Console.WriteLine("");
                }
            }

            connType.GetMethod("Close").Invoke(conn, null);
            Console.WriteLine("Done");
        }
        catch (Exception ex)
        {
            Console.WriteLine("ERROR: " + ex.Message);
            if (ex.InnerException != null)
                Console.WriteLine("INNER: " + ex.InnerException.Message);
            Console.WriteLine(ex.StackTrace);
        }
    }
}
