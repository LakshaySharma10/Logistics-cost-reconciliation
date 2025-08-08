'use client'

import { FileUpload } from "@/components/file-upload";
import { useState } from "react";
import { PieChart, Pie, Tooltip, Cell, Legend, ResponsiveContainer } from 'recharts';
import { sora400 } from "@/lib/font-utils";

const COLORS = ['#8884d8', '#82ca9d', '#ffc658'];

export default function Home() {
  const [files, setFiles] = useState<File[]>([]);
  const [report, setReport] = useState<any>(null);

  const handleFileUpload = async (files: File[]) => {
    setFiles(files);
    const formData = new FormData();
    formData.append("file", files[0]);

    const uploadRes = await fetch("http://localhost:8000/api/upload/", {
      method: "POST",
      body: formData,
    });

    if (!uploadRes.ok) return;

    const optimizeRes = await fetch("http://localhost:8000/api/optimize-loads/", {
      method: "POST",
    });

    const reportRes = await fetch("http://localhost:8000/api/export/json/?total_cost=3000");
    const reportData = await reportRes.json();
    setReport(reportData);
  };

  const downloadCSV = async () => {
    const res = await fetch("http://localhost:8000/api/export/csv/?total_cost=3000");
    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", "");
    document.body.appendChild(link);
    link.click();
    link.remove();
  };

  const computeCompanyLoads = (trucks: any[]) => {
    const loadMap: Record<string, number> = {};
    trucks.forEach(truck => {
      const company = truck.company;
      loadMap[company] = (loadMap[company] || 0) + truck.assigned_load;
    });
    return loadMap;
  };

  const companyLoads = report ? computeCompanyLoads(report.trucks) : {};

  const pieData = report
    ? Object.entries(report.company_costs).map(([company, cost]) => ({
      name: company,
      value: parseFloat(cost as string),
    }))
    : [];

  return (
    <main className={`${sora400.className} p-4 sm:p-6 lg:p-8 text-white bg-black min-h-screen`}>
      <h1 className="text-2xl sm:text-3xl font-bold mt-6 text-center">
        Logistics Cost Reconciliation
      </h1>

      <div className="flex justify-center mb-6">
        <FileUpload onChange={handleFileUpload} />
      </div>

      {report && (
        <>
          <div className="mb-10">
            <h2 className="text-xl sm:text-2xl font-bold mb-4 text-center sm:text-left">
              Company Cost Breakdown (After Optimization)
            </h2>

            <div className="overflow-x-auto">
              <table className="table-auto w-full border border-white mb-4 min-w-full">
                <thead className="bg-gray-100 text-black">
                  <tr>
                    <th className="border border-white px-2 sm:px-4 py-2 text-sm sm:text-base">Company</th>
                    <th className="border border-white px-2 sm:px-4 py-2 text-sm sm:text-base">Assigned Load</th>
                    <th className="border border-white px-2 sm:px-4 py-2 text-sm sm:text-base">Cost Share</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(report.company_costs).map(([company, cost]) => (
                    <tr key={company}>
                      <td className="border border-white px-2 sm:px-4 py-2 text-sm sm:text-base">{company}</td>
                      <td className="border border-white px-2 sm:px-4 py-2 text-sm sm:text-base">{companyLoads[company] || 0}</td>
                      <td className="border border-white px-2 sm:px-4 py-2 text-sm sm:text-base">{cost as string}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Truck-wise Load Distribution */}
            <div className="mb-10">
              <h2 className="text-xl sm:text-2xl font-bold mb-4 text-center sm:text-left">
                Truck Load Distribution
              </h2>

              <div className="overflow-x-auto">
                <table className="table-auto w-full border border-white mb-4 min-w-full">
                  <thead className="bg-gray-100 text-black">
                    <tr>
                      <th className="border border-white px-2 sm:px-4 py-2 text-sm sm:text-base">Truck ID</th>
                      <th className="border border-white px-2 sm:px-4 py-2 text-sm sm:text-base">Company</th>
                      <th className="border border-white px-2 sm:px-4 py-2 text-sm sm:text-base">Assigned Load</th>
                      <th className="border border-white px-2 sm:px-4 py-2 text-sm sm:text-base">Capacity</th>
                      <th className="border border-white px-2 sm:px-4 py-2 text-sm sm:text-base">Unused Space</th>
                    </tr>
                  </thead>
                  <tbody>
                    {report.trucks.map((truck: any, idx: number) => (
                      <tr key={idx}>
                        <td className="border border-white px-2 sm:px-4 py-2 text-sm sm:text-base">{truck.truck_id || `Truck ${idx + 1}`}</td>
                        <td className="border border-white px-2 sm:px-4 py-2 text-sm sm:text-base">{truck.company}</td>
                        <td className="border border-white px-2 sm:px-4 py-2 text-sm sm:text-base">{truck.assigned_load}</td>
                        <td className="border border-white px-2 sm:px-4 py-2 text-sm sm:text-base">{truck.capacity}</td>
                        <td className="border border-white px-2 sm:px-4 py-2 text-sm sm:text-base">{truck.capacity - truck.assigned_load}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>


            {pieData.length > 0 && (
              <div className="flex justify-center w-full">
                <div className="w-full max-w-lg">
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={pieData}
                        cx="50%"
                        cy="50%"
                        outerRadius="80%"
                        dataKey="value"
                        label
                      >
                        {pieData.map((_, index) => (
                          <Cell key={index} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </div>
            )}
          </div>

          <div className="text-center">
            <button
              className="px-4 py-2 cursor-pointer bg-blue-500 text-white rounded hover:bg-blue-700 text-sm sm:text-base"
              onClick={downloadCSV}
            >
              Download Report
            </button>
          </div>
        </>
      )}
    </main>
  );
}
