using System;
using System.Data;
using System.Reflection;
using System.IO;
using System.Text;
using System.Collections.Generic;

class Program
{
    static string EscapeJson(string str)
    {
        if (string.IsNullOrEmpty(str)) return "";
        return str.Replace("\\", "\\\\").Replace("\"", "\\\"").Replace("\n", "\\n").Replace("\r", "");
    }

    static void Main(string[] args)
    {
        if (args.Length < 2)
        {
            Console.WriteLine("Usage: export_jiandanke.exe <backup_file.bak> <output.json>");
            return;
        }

        string dbFile = args[0];
        string outputFile = args[1];

        if (!File.Exists(dbFile))
        {
            Console.WriteLine("ERROR: Database file not found: " + dbFile);
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

            // Query 1: Get all goods
            object cmdGoods = Activator.CreateInstance(cmdType, new object[] {
                "SELECT goods_Id, goods_Name, goods_Code, goods_Inventory, goods_Cost, goods_Price, goods_Location, goods_Remark, goods_Cate FROM t_Goods WHERE goods_Enabled=1;",
                conn
            });

            // Query 2: Get outgoing quantities (Sales type from t_BusinessDetail)
            object cmdSales = Activator.CreateInstance(cmdType, new object[] {
                @"SELECT d.detail_Goods, SUM(d.detail_Count) as total_out
                  FROM t_BusinessDetail d
                  INNER JOIN t_Business b ON d.detail_Business = b.business_Id
                  WHERE d.detail_Type = 'Sales' AND b.business_Status != 'Cancelled'
                  GROUP BY d.detail_Goods;",
                conn
            });

            // Build sales lookup
            Dictionary<string, double> salesMap = new Dictionary<string, double>();
            using (IDataReader salesReader = (IDataReader)cmdType.GetMethod("ExecuteReader", new Type[0]).Invoke(cmdSales, null))
            {
                while (salesReader.Read())
                {
                    string goodsId = salesReader[0].ToString();
                    double totalOut = salesReader[1] == DBNull.Value ? 0 : Convert.ToDouble(salesReader[1]);
                    salesMap[goodsId] = totalOut;
                }
            }

            // Build goods JSON with sales data
            StringBuilder json = new StringBuilder();
            json.AppendLine("[");
            bool first = true;
            
            using (IDataReader reader = (IDataReader)cmdType.GetMethod("ExecuteReader", new Type[0]).Invoke(cmdGoods, null))
            {
                while (reader.Read())
                {
                    if (!first) json.AppendLine(",");
                    first = false;
                    
                    json.Append("  {");
                    
                    string goodsId = reader[0].ToString();
                    string name = EscapeJson(reader[1] == DBNull.Value ? "" : reader[1].ToString());
                    string code = EscapeJson(reader[2] == DBNull.Value ? "" : reader[2].ToString());
                    string stock = reader[3] == DBNull.Value ? "0" : reader[3].ToString();
                    if (string.IsNullOrEmpty(stock)) stock = "0";
                    string cost = reader[4] == DBNull.Value ? "0" : reader[4].ToString();
                    if (string.IsNullOrEmpty(cost)) cost = "0";
                    string price = reader[5] == DBNull.Value ? "0" : reader[5].ToString();
                    if (string.IsNullOrEmpty(price)) price = "0";
                    string location = EscapeJson(reader[6] == DBNull.Value ? "" : reader[6].ToString());
                    string remark = EscapeJson(reader[7] == DBNull.Value ? "" : reader[7].ToString());
                    string cate = EscapeJson(reader[8] == DBNull.Value ? "" : reader[8].ToString());

                    double soldQty = salesMap.ContainsKey(goodsId) ? salesMap[goodsId] : 0;

                    json.Append("\"商品名称\": \"").Append(name).Append("\", ");
                    json.Append("\"货号\": \"").Append(code).Append("\", ");
                    json.Append("\"条码\": \"").Append(code).Append("\", ");
                    json.Append("\"分类\": \"").Append(cate).Append("\", ");
                    json.Append("\"库存数量\": ").Append(stock).Append(", ");
                    json.Append("\"出库数量\": ").Append(soldQty.ToString("F0")).Append(", ");
                    json.Append("\"参考进价\": ").Append(cost).Append(", ");
                    json.Append("\"最后进价\": ").Append(cost).Append(", ");
                    json.Append("\"参考售价\": ").Append(price).Append(", ");
                    json.Append("\"最后售价\": ").Append(price).Append(", ");
                    json.Append("\"库位\": \"").Append(location).Append("\", ");
                    json.Append("\"备注\": \"").Append(remark).Append("\"");
                    
                    json.Append("}");
                }
            }
            
            json.AppendLine();
            json.AppendLine("]");
            
            File.WriteAllText(outputFile, json.ToString(), Encoding.UTF8);
            Console.WriteLine("SUCCESS: Exported to " + outputFile);
        }
        catch (Exception ex)
        {
            Console.WriteLine("FAILED: " + ex.Message);
        }
    }
}
