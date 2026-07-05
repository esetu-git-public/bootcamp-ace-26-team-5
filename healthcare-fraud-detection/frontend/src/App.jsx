import React, { useState, useEffect } from 'react';
import { 
  ShieldAlert, 
  CheckCircle, 
  AlertTriangle, 
  Activity, 
  DollarSign, 
  FileText, 
  PlusCircle, 
  Loader2 
} from 'lucide-react';

function App() {
  const [claims, setClaims] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [newClaim, setNewClaim] = useState({
    providerId: '',
    insurancePlan: '',
    claimAmount: '',
    diagnosisCode: ''
  });

  useEffect(() => {
    fetchClaims();
  }, []);

  const fetchClaims = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:5000/api/claims'); 
      const data = await response.json();
      setClaims(data);
    } catch (error) {
      console.error("Error fetching claims:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setNewClaim({ ...newClaim, [name]: value });
  };

  const handleSubmitClaim = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const response = await fetch('http://localhost:5000/api/claims', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newClaim)
      });
      
      if (response.ok) {
        await fetchClaims();
        setNewClaim({ providerId: '', insurancePlan: '', claimAmount: '', diagnosisCode: '' });
      }
    } catch (error) {
      console.error("Error submitting claim:", error);
    } finally {
      setSubmitting(false);
    }
  };

  // Math Metric Computations
  const totalClaims = claims.length;
  const flaggedClaims = claims.filter(c => c.isFraud).length;
  const totalAmount = claims.reduce((sum, c) => sum + Number(c.claimAmount || 0), 0);
  const fraudRate = totalClaims > 0 ? ((flaggedClaims / totalClaims) * 100).toFixed(1) : 0;

  return (
    <div className="flex min-h-screen bg-slate-50 text-slate-800 font-sans">
      
      {/* Sidebar Layout panel */}
      <aside className="w-64 bg-slate-900 text-white flex flex-col justify-between hidden md:flex border-r border-slate-800">
        <div>
          <div className="p-6 flex items-center gap-3 border-b border-slate-800">
            <ShieldAlert className="h-8 w-8 text-blue-500" />
            <span className="font-bold text-lg tracking-wide bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent">
              ShieldAI Health
            </span>
          </div>
          <nav className="p-4 space-y-2">
            <a href="#" className="flex items-center gap-3 px-4 py-3 rounded-lg bg-blue-600 text-white font-medium transition">
              <Activity className="h-5 w-5" /> Live Overview
            </a>
          </nav>
        </div>
        <div className="p-4 border-t border-slate-800 text-xs text-slate-400 text-center">
          Enterprise Security Active
        </div>
      </aside>

      {/* Main Workspace Frame */}
      <div className="flex-1 flex flex-col overflow-hidden">
        
        {/* Top App Bar Header */}
        <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-8 shadow-sm">
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold text-slate-900">Fraud Detection System</h1>
            <span className="bg-blue-50 text-blue-700 text-xs font-semibold px-2.5 py-0.5 rounded-full border border-blue-200">Live</span>
          </div>
          <div className="flex items-center gap-4">
            <div className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></div>
            <span className="text-sm font-medium text-slate-600">Model Pipeline Connected</span>
          </div>
        </header>

        {/* Dynamic Body Content Grid */}
        <main className="flex-1 overflow-y-auto p-8 space-y-8">
          
          {/* Statistical Analytics Highlight Row */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-500 font-medium">Total Audited</p>
                <h3 className="text-2xl font-bold mt-1 text-slate-900">{totalClaims}</h3>
              </div>
              <div className="p-3 rounded-lg bg-blue-50 text-blue-600"><FileText className="h-6 w-6" /></div>
            </div>

            <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-500 font-medium">Flagged Claims</p>
                <h3 className="text-2xl font-bold mt-1 text-red-600">{flaggedClaims}</h3>
              </div>
              <div className="p-3 rounded-lg bg-red-50 text-red-600"><AlertTriangle className="h-6 w-6" /></div>
            </div>

            <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-500 font-medium">Audited Volume</p>
                <h3 className="text-2xl font-bold mt-1 text-slate-900">${totalAmount.toLocaleString()}</h3>
              </div>
              <div className="p-3 rounded-lg bg-emerald-50 text-emerald-600"><DollarSign className="h-6 w-6" /></div>
            </div>

            <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-500 font-medium">Anomaly Rate</p>
                <h3 className="text-2xl font-bold mt-1 text-slate-900">{fraudRate}%</h3>
              </div>
              <div className="p-3 rounded-lg bg-indigo-50 text-indigo-600"><ShieldAlert className="h-6 w-6" /></div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
            
            {/* Input Submission Panel Card */}
            <section className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden lg:col-span-1">
              <div className="bg-slate-50 px-6 py-4 border-b border-slate-200">
                <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
                  <PlusCircle className="h-5 w-5 text-blue-600" /> Inspect New Claim
                </h2>
              </div>
              <form onSubmit={handleSubmitClaim} className="p-6 space-y-4">
                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">Provider ID</label>
                  <input type="text" name="providerId" value={newClaim.providerId} onChange={handleInputChange} required className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition" placeholder="e.g. PROV-72A" />
                </div>
                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">Insurance Plan</label>
                  <input type="text" name="insurancePlan" value={newClaim.insurancePlan} onChange={handleInputChange} required className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition" placeholder="e.g. Choice Premium" />
                </div>
                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">Claim Cost ($)</label>
                  <input type="number" name="claimAmount" value={newClaim.claimAmount} onChange={handleInputChange} required className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition" placeholder="0.00" />
                </div>
                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">Diagnosis Code</label>
                  <input type="text" name="diagnosisCode" value={newClaim.diagnosisCode} onChange={handleInputChange} required className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition" placeholder="e.g. M54.5" />
                </div>
                <button type="submit" disabled={submitting} className="w-full mt-2 bg-slate-950 text-white font-medium py-2.5 px-4 rounded-lg hover:bg-slate-800 focus:ring-4 focus:ring-slate-950/20 transition flex items-center justify-center gap-2 disabled:opacity-50">
                  {submitting ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin" /> Verifying...
                    </>
                  ) : 'Run Anomaly Check'}
                </button>
              </form>
            </section>

            {/* Monitoring Logs Data Table Grid Card */}
            <section className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden lg:col-span-2">
              <div className="bg-slate-50 px-6 py-4 border-b border-slate-200 flex justify-between items-center">
                <h2 className="text-base font-bold text-slate-900">Recent Stream Pipeline</h2>
                <button onClick={fetchClaims} className="text-xs font-medium text-blue-600 hover:underline">Sync System</button>
              </div>

              {loading ? (
                <div className="flex flex-col items-center justify-center py-20 gap-3 text-slate-400">
                  <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
                  <p className="text-sm font-medium">Streaming network records...</p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full border-collapse text-left text-sm">
                    <thead>
                      <tr className="bg-slate-50 border-b border-slate-200 text-slate-400 font-semibold tracking-wider text-xs uppercase">
                        <th className="px-6 py-4">ID</th>
                        <th className="px-6 py-4">Provider</th>
                        <th className="px-6 py-4">Cost</th>
                        <th className="px-6 py-4">Diagnosis</th>
                        <th className="px-6 py-4">Status evaluation</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {claims.map((claim) => (
                        <tr key={claim.id} className="hover:bg-slate-50/70 transition">
                          <td className="px-6 py-4 font-mono text-xs text-slate-500">#{claim.id}</td>
                          <td className="px-6 py-4 font-medium text-slate-900">{claim.providerId}</td>
                          <td className="px-6 py-4 font-semibold text-slate-900">${Number(claim.claimAmount).toLocaleString()}</td>
                          <td className="px-6 py-4"><span className="bg-slate-100 px-2 py-1 rounded text-xs font-mono text-slate-600">{claim.diagnosisCode}</span></td>
                          <td className="px-6 py-4">
                            {claim.isFraud ? (
                              <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-50 border border-rose-200 text-rose-700">
                                <AlertTriangle className="h-3.5 w-3.5" /> Flagged Threat
                              </span>
                            ) : (
                              <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-50 border border-emerald-200 text-emerald-700">
                                <CheckCircle className="h-3.5 w-3.5" /> Clear
                              </span>
                            )}
                          </td>
                        </tr>
                      ))}
                      {claims.length === 0 && (
                        <tr>
                          <td colSpan="5" className="px-6 py-12 text-center text-slate-400">
                            No records found. Submit data using the inspection form.
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              )}
            </section>

          </div>
        </main>
      </div>
    </div>
  );
}

export default App;
