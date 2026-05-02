import { useState, useEffect } from "react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend
} from "recharts";

const API_BASE = "http://localhost:8000";

const COLORS = {
  primary: "#185FA5",
  secondary: "#1D9E75",
  accent: "#D85A30",
  warning: "#BA7517",
  purple: "#534AB7",
};

const PIE_COLORS = ["#378ADD", "#1D9E75", "#EF9F27", "#D85A30", "#534AB7"];

function StatCard({ label, value, sub, color }) {
  return (
    <div style={{
      background: "var(--card-bg)",
      borderRadius: 12,
      padding: "16px 20px",
      border: "0.5px solid var(--border-color)",
    }}>
      <div style={{ fontSize: 11, color: "#888", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 8 }}>
        {label}
      </div>
      <div style={{ fontSize: 28, fontWeight: 600, color: color || "#185FA5", lineHeight: 1 }}>
        {value}
      </div>
      {sub && <div style={{ fontSize: 12, color: "#999", marginTop: 6 }}>{sub}</div>}
    </div>
  );
}

function SectionHeader({ title, subtitle }) {
  return (
    <div style={{ marginBottom: 16 }}>
      <h2 style={{ fontSize: 15, fontWeight: 600, color: "#1a1a1a", margin: 0 }}>{title}</h2>
      {subtitle && <p style={{ fontSize: 12, color: "#888", margin: "4px 0 0" }}>{subtitle}</p>}
    </div>
  );
}

export default function App() {
  const [summary, setSummary] = useState(null);
  const [cityData, setCityData] = useState([]);
  const [catData, setCatData] = useState([]);
  const [sourceData, setSourceData] = useState([]);
  const [listings, setListings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchAll() {
      try {
        setLoading(true);
        const [summaryRes, cityRes, catRes, srcRes, listRes] = await Promise.all([
          fetch(`${API_BASE}/api/dashboard/summary`),
          fetch(`${API_BASE}/api/dashboard/city-wise`),
          fetch(`${API_BASE}/api/dashboard/category-wise`),
          fetch(`${API_BASE}/api/dashboard/source-wise`),
          fetch(`${API_BASE}/api/listings?limit=20`),
        ]);

        setSummary(await summaryRes.json());
        setCityData(await cityRes.json());
        setCatData(await catRes.json());
        setSourceData(await srcRes.json());
        const listData = await listRes.json();
        setListings(listData.data || []);
      } catch (err) {
        setError("Failed to connect to API. Make sure FastAPI is running on port 8000.");
      } finally {
        setLoading(false);
      }
    }
    fetchAll();
  }, []);

  if (loading) {
    return (
      <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "100vh" }}>
        <div style={{ textAlign: "center" }}>
          <div style={{ fontSize: 24, fontWeight: 600, color: "#185FA5" }}>Loading dashboard...</div>
          <div style={{ fontSize: 14, color: "#888", marginTop: 8 }}>Connecting to FastAPI backend</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "100vh" }}>
        <div style={{ textAlign: "center", maxWidth: 400 }}>
          <div style={{ fontSize: 48, marginBottom: 16 }}>⚠️</div>
          <div style={{ fontSize: 18, fontWeight: 600, color: "#D85A30" }}>Connection Error</div>
          <div style={{ fontSize: 14, color: "#888", marginTop: 8 }}>{error}</div>
          <code style={{ display: "block", marginTop: 16, padding: 12, background: "#f5f5f5", borderRadius: 8, fontSize: 13 }}>
            uvicorn main:app --reload --port 8000
          </code>
        </div>
      </div>
    );
  }

  const sourcePct = (count) => ((count / (summary?.total_listings || 1)) * 100).toFixed(1);

  return (
    <div style={{ minHeight: "100vh", background: "#F8F9FC", fontFamily: "system-ui, -apple-system, sans-serif" }}>
      {/* Header */}
      <header style={{
        background: "white",
        borderBottom: "0.5px solid #e8e8e8",
        padding: "14px 32px",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        position: "sticky",
        top: 0,
        zIndex: 100,
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <div style={{
            width: 36, height: 36,
            background: "#185FA5",
            borderRadius: 10,
            display: "flex", alignItems: "center", justifyContent: "center",
          }}>
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <rect x="2" y="11" width="3" height="7" rx="1" fill="white" />
              <rect x="7" y="6" width="3" height="12" rx="1" fill="white" />
              <rect x="12" y="2" width="3" height="16" rx="1" fill="white" />
            </svg>
          </div>
          <div>
            <div style={{ fontWeight: 700, fontSize: 16, color: "#1a1a1a" }}>Business Listings Dashboard</div>
            <div style={{ fontSize: 11, color: "#999" }}>India · FastAPI + MySQL + React</div>
          </div>
        </div>
        <div style={{
          fontSize: 12,
          background: "#E6F1FB",
          color: "#185FA5",
          padding: "5px 14px",
          borderRadius: 20,
          fontWeight: 500,
        }}>
          {summary?.total_listings} listings collected
        </div>
      </header>

      <main style={{ padding: "28px 32px", maxWidth: 1280, margin: "0 auto" }}>
        {/* Summary stats */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12, marginBottom: 28 }}>
          <StatCard label="Total Listings" value={summary?.total_listings?.toLocaleString()} sub="Scraped from directories" color="#185FA5" />
          <StatCard label="Cities Covered" value={summary?.total_cities} sub="Pan-India coverage" color="#1D9E75" />
          <StatCard label="Categories" value={summary?.total_categories} sub="Business types" color="#BA7517" />
          <StatCard label="Data Sources" value={summary?.total_sources} sub="Justdial, Sulekha & more" color="#993C1D" />
        </div>

        {/* City-wise chart */}
        <div style={{
          background: "white",
          border: "0.5px solid #e8e8e8",
          borderRadius: 14,
          padding: "20px 24px",
          marginBottom: 16,
        }}>
          <SectionHeader title="City-wise business count" subtitle="All 20 cities ranked by total listings" />
          <ResponsiveContainer width="100%" height={320}>
            <BarChart data={cityData} layout="vertical" margin={{ left: 80, right: 20, top: 4, bottom: 4 }}>
              <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#f0f0f0" />
              <XAxis type="number" tick={{ fontSize: 11, fill: "#999" }} axisLine={false} tickLine={false} />
              <YAxis type="category" dataKey="name" tick={{ fontSize: 11, fill: "#555" }} axisLine={false} tickLine={false} width={76} />
              <Tooltip
                contentStyle={{ fontSize: 12, borderRadius: 8, border: "0.5px solid #e8e8e8", boxShadow: "0 4px 12px rgba(0,0,0,0.08)" }}
                formatter={(v) => [`${v} listings`, "Count"]}
              />
              <Bar dataKey="count" fill="#185FA5" radius={[0, 3, 3, 0]}
                label={{ position: "right", fontSize: 10, fill: "#999" }} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Category + Source */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginBottom: 16 }}>
          <div style={{
            background: "white", border: "0.5px solid #e8e8e8",
            borderRadius: 14, padding: "20px 24px",
          }}>
            <SectionHeader title="Category-wise count" subtitle="Top 10 business categories" />
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={catData.slice(0, 10)} layout="vertical" margin={{ left: 110, right: 20, top: 4, bottom: 4 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#f0f0f0" />
                <XAxis type="number" tick={{ fontSize: 10, fill: "#999" }} axisLine={false} tickLine={false} />
                <YAxis type="category" dataKey="name" tick={{ fontSize: 10, fill: "#555" }} axisLine={false} tickLine={false} width={106} />
                <Tooltip contentStyle={{ fontSize: 12, borderRadius: 8, border: "0.5px solid #e8e8e8" }} formatter={(v) => [`${v} listings`, "Count"]} />
                <Bar dataKey="count" radius={[0, 3, 3, 0]}>
                  {catData.slice(0, 10).map((_, i) => (
                    <Cell key={i} fill={["#185FA5","#1D9E75","#D85A30","#BA7517","#534AB7","#378ADD","#5DCAA5","#EF9F27","#D4537E","#639922"][i % 10]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div style={{
            background: "white", border: "0.5px solid #e8e8e8",
            borderRadius: 14, padding: "20px 24px",
          }}>
            <SectionHeader title="Source-wise distribution" subtitle="Listings by data source" />
            <ResponsiveContainer width="100%" height={240}>
              <PieChart>
                <Pie data={sourceData} cx="50%" cy="50%" innerRadius={55} outerRadius={95}
                  dataKey="count" nameKey="name" paddingAngle={2}
                  label={({ name, count }) => `${name}: ${count}`} labelLine={false}
                  fontSize={11}>
                  {sourceData.map((_, i) => (
                    <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(v, name) => [`${v} listings (${sourcePct(v)}%)`, name]} contentStyle={{ fontSize: 12, borderRadius: 8 }} />
                <Legend
                  formatter={(value, entry) => (
                    <span style={{ fontSize: 11, color: "#555" }}>{value}: {sourcePct(entry.payload.count)}%</span>
                  )}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Listings table */}
        <div style={{
          background: "white", border: "0.5px solid #e8e8e8",
          borderRadius: 14, padding: "20px 24px",
        }}>
          <SectionHeader title="Sample listings" subtitle="First 20 records from listing_master table" />
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 12 }}>
              <thead>
                <tr style={{ borderBottom: "0.5px solid #eee" }}>
                  {["ID", "Business Name", "Category", "City", "Phone", "Source", "Address"].map(h => (
                    <th key={h} style={{ textAlign: "left", padding: "8px 12px", fontSize: 11, color: "#888", fontWeight: 600, background: "#fafafa", whiteSpace: "nowrap" }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {listings.map((row, i) => (
                  <tr key={row.id} style={{ borderBottom: "0.5px solid #f5f5f5", background: i % 2 === 0 ? "white" : "#fafafa" }}>
                    <td style={{ padding: "9px 12px", color: "#aaa" }}>{row.id}</td>
                    <td style={{ padding: "9px 12px", fontWeight: 500, color: "#1a1a1a" }}>{row.business_name}</td>
                    <td style={{ padding: "9px 12px" }}>
                      <span style={{ background: "#E6F1FB", color: "#0C447C", fontSize: 10, padding: "2px 8px", borderRadius: 10, fontWeight: 500 }}>
                        {row.category}
                      </span>
                    </td>
                    <td style={{ padding: "9px 12px", color: "#555" }}>{row.city}</td>
                    <td style={{ padding: "9px 12px", color: "#888", fontFamily: "monospace", fontSize: 11 }}>{row.phone || "N/A"}</td>
                    <td style={{ padding: "9px 12px" }}>
                      <span style={{ background: "#EAF3DE", color: "#27500A", fontSize: 10, padding: "2px 8px", borderRadius: 10, fontWeight: 500 }}>
                        {row.source}
                      </span>
                    </td>
                    <td style={{ padding: "9px 12px", color: "#888", maxWidth: 200, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{row.address || "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Footer */}
        <div style={{ marginTop: 20, padding: "12px 0", borderTop: "0.5px solid #e8e8e8", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <div style={{ fontSize: 11, color: "#aaa" }}>Business Listings Dashboard · FastAPI + MySQL + React.js + Recharts</div>
          <div style={{ display: "flex", gap: 8 }}>
            {["GET /api/dashboard/city-wise", "GET /api/dashboard/category-wise", "GET /api/dashboard/source-wise"].map(api => (
              <code key={api} style={{ fontSize: 10, background: "#EAF3DE", color: "#27500A", padding: "3px 8px", borderRadius: 8 }}>{api}</code>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}
