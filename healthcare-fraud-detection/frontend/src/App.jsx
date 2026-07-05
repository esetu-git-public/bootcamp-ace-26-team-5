import React, { useState } from 'react';

export default function App() {
  const [claims, setClaims] = useState([
    { id: 'CLM-9042', provider: 'PROV-21A', cost: 1420.00, diagnosis: 'M54.5', status: 'Passed', anomalyScore: 12 },
    { id: 'CLM-9043', provider: 'PROV-72A', cost: 8900.00, diagnosis: 'R07.9', status: 'Flagged', anomalyScore: 89 },
    { id: 'CLM-9044', provider: 'PROV-11B', cost: 310.00, diagnosis: 'J06.9', status: 'Passed', anomalyScore: 5 },
  ]);

  const [provider, setProvider] = useState('');
  const [plan, setPlan] = useState('');
  const [cost, setCost] = useState('');
  const [diagnosis, setDiagnosis] = useState('');

  const handleCheck = (e) => {
    e.preventDefault();
    if (!provider || !cost || !diagnosis) return;

    // Simulate an AI calculation
    const score = Math.floor(Math.random() * 100);
    const newClaim = {
      id: `CLM-${Math.floor(1000 + Math.random() * 9000)}`,
      provider,
      cost: parseFloat(cost),
      diagnosis,
      status: score > 70 ? 'Flagged' : 'Passed',
      anomalyScore: score
    };

    setClaims([newClaim, ...claims]);
    setProvider('');
    setCost('');
    setDiagnosis('');
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans selection:bg-cyan-500 selection:text-slate-950">
      {/* Glow Effects */}
      <div className="absolute top-0 left-1/4 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-10 right-1/4 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />

      {/* Header */}
      <header className="border-b border-slate-800/80 backdrop-blur-md sticky top-0 z-50 bg-slate-950/80">
        <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-cyan-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
              <span className="text-xl font-black text-white">S</span>
            </div>
            <div>
              <h1 className="text-lg font-bold tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
                ShieldAI Health
              </h1>
              <p className="text-xs text-cyan-400 font-medium tracking-widest uppercase">Live Overview</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <span className="flex h-2 w-2 relative">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400 bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-full">
              Enterprise Active
            </span>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-10 grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left Column: Metrics & Form */}
        <div className="lg:col-span-1 flex flex-col gap-8">
          
          {/* Quick Metrics */}
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-slate-900/50 border border-slate-800/80 rounded-2xl p-5 backdrop-blur-sm">
              <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">Anomaly Rate</p>
              <p className="text-3xl font-bold tracking-tight text-rose-400 mt-2">24.3%</p>
            </div>
            <div className="bg-slate-900/50 border border-slate-800/80 rounded-2xl p-5 backdrop-blur-sm">
              <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">Audited Volume</p>
              <p className="text-3xl font-bold tracking-tight text-cyan-400 mt-2">$14.2k</p>
            </div>
          </div>

          {/* Form Card */}
          <div className="bg-gradient-to-b from-slate-900 to-slate-950 border border-slate-800 rounded-3xl p-6 shadow-xl relative overflow-hidden">
            <h2 className="text-xl font-bold text-white mb-1">Inspect New Claim</h2>
            <p className="text-xs text-slate-400 mb-6">Analyze metrics instantly with the ShieldAI pipeline.</p>
            
            <form onSubmit={handleCheck} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Provider ID</label>
                <input 
                  type="text" value={provider} onChange={e => setProvider(e.target.value)}
                  placeholder="e.g. PROV-72A" 
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-100 focus:outline-none focus:border-cyan-500 transition-colors"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Claim Cost ($)</label>
                <input 
                  type="number" value={cost} onChange={e => setCost(e.target.value)}
                  placeholder="0.00" 
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-100 focus:outline-none focus:border-cyan-500 transition-colors"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Diagnosis Code</label>
                <input 
                  type="text" value={diagnosis} onChange={e => setDiagnosis(e.target.value)}
                  placeholder="e.g. M54.5" 
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-100 focus:outline-none focus:border-cyan-500 transition-colors"
                />
              </div>

              <button type="submit" className="w-full mt-2 bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-white font-semibold text-sm py-3.5 px-4 rounded-xl shadow-lg shadow-cyan-500/20 transition-all active:scale-[0.98]">
                Run Anomaly Check
              </button>
            </form>
          </div>
        </div>

        {/* Right Column: Active Live Stream Pipeline */}
        <div className="lg:col-span-2 bg-slate-900/30 border border-slate-800/80 rounded-3xl p-6 backdrop-blur-sm flex flex-col">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-xl font-bold text-white">Live Audit Stream</h2>
              <p className="text-xs text-slate-400">Real-time evaluating scoring engine active.</p>
            </div>
          </div>

          <div className="flex-1 overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-800 text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  <th className="pb-3 pl-4">Claim ID</th>
                  <th className="pb-3">Provider</th>
                  <th className="pb-3">Cost</th>
                  <th className="pb-3">Diagnosis</th>
                  <th className="pb-3 text-right pr-4">AI Score</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/50 text-sm">
                {claims.map((claim) => (
                  <tr key={claim.id} className="hover:bg-slate-800/20 transition-colors group">
                    <td className="py-4 pl-4 font-mono text-cyan-400 font-medium">{claim.id}</td>
                    <td className="py-4 text-slate-300">{claim.provider}</td>
                    <td className="py-4 font-medium text-slate-100">${claim.cost.toFixed(2)}</td>
                    <td className="py-4"><span className="bg-slate-800 px-2 py-1 rounded text-xs font-mono text-slate-400">{claim.diagnosis}</span></td>
                    <td className="py-4 text-right pr-4">
                      <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold ${
                        claim.status === 'Flagged' 
                          ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20' 
                          : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                      }`}>
                        {claim.anomalyScore}% {claim.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

      </main>
    </div>
  );
}
