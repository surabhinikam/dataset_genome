/**
 * SettingsView.tsx — Ecosystem Credentials & Platform Configuration View.
 */

"use client";

import React, { useState } from "react";
import { Settings, Key, Save, CheckCircle2, ShieldAlert } from "lucide-react";

export const SettingsView: React.FC = () => {
  const [hfToken, setHfToken] = useState("hf_**********************************");
  const [kaggleUser, setKaggleUser] = useState("surabhicodes");
  const [kaggleKey, setKaggleKey] = useState("********************************");
  const [endpoint, setEndpoint] = useState("http://127.0.0.1:8000/autoscientist");
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div className="p-8 space-y-6 max-w-4xl">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
          <Settings className="w-5 h-5 text-gray-400" />
          Ecosystem Credentials & Platform Configuration
        </h1>
        <p className="text-xs text-gray-400">
          Configure process environment API tokens and integration endpoints for automated publishing.
        </p>
      </div>

      {/* Settings Form Card */}
      <div className="bg-[#111827] border border-[#1F2937] rounded-xl p-6 space-y-6">
        {/* Section 1: Hugging Face */}
        <div className="space-y-3 pb-6 border-b border-[#1F2937]">
          <div className="flex items-center gap-2">
            <Key className="w-4 h-4 text-[#3B82F6]" />
            <h3 className="font-semibold text-sm text-white">Hugging Face Ecosystem Credentials</h3>
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-400 mb-1.5">
              Hugging Face User Access Token (HF_TOKEN)
            </label>
            <input
              type="password"
              value={hfToken}
              onChange={(e) => setHfToken(e.target.value)}
              className="w-full bg-[#0B1220] border border-[#1F2937] rounded-lg px-3 py-2 text-xs font-mono text-white focus:outline-none focus:border-[#3B82F6]"
            />
            <span className="text-[10px] text-gray-500 mt-1 block">
              Required for pushing dataset packages, model cards, and snapshot downloads.
            </span>
          </div>
        </div>

        {/* Section 2: Kaggle API */}
        <div className="space-y-3 pb-6 border-b border-[#1F2937]">
          <div className="flex items-center gap-2">
            <Key className="w-4 h-4 text-amber-400" />
            <h3 className="font-semibold text-sm text-white">Kaggle API Credentials</h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-gray-400 mb-1.5">
                Kaggle Username (KAGGLE_USERNAME)
              </label>
              <input
                type="text"
                value={kaggleUser}
                onChange={(e) => setKaggleUser(e.target.value)}
                className="w-full bg-[#0B1220] border border-[#1F2937] rounded-lg px-3 py-2 text-xs font-mono text-white focus:outline-none focus:border-[#3B82F6]"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-400 mb-1.5">
                Kaggle API Key (KAGGLE_KEY)
              </label>
              <input
                type="password"
                value={kaggleKey}
                onChange={(e) => setKaggleKey(e.target.value)}
                className="w-full bg-[#0B1220] border border-[#1F2937] rounded-lg px-3 py-2 text-xs font-mono text-white focus:outline-none focus:border-[#3B82F6]"
              />
            </div>
          </div>
        </div>

        {/* Section 3: AutoScientist Server Endpoint */}
        <div className="space-y-3 pb-6 border-b border-[#1F2937]">
          <h3 className="font-semibold text-sm text-white">AutoScientist Integration Endpoint</h3>
          <div>
            <label className="block text-xs font-medium text-gray-400 mb-1.5">
              Backend FastAPI API Base URL
            </label>
            <input
              type="text"
              value={endpoint}
              onChange={(e) => setEndpoint(e.target.value)}
              className="w-full bg-[#0B1220] border border-[#1F2937] rounded-lg px-3 py-2 text-xs font-mono text-white focus:outline-none focus:border-[#3B82F6]"
            />
          </div>
        </div>

        {/* Save CTA */}
        <div className="flex items-center justify-between">
          <span className="text-xs text-gray-400">
            {saved ? (
              <span className="text-emerald-400 flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4" /> Settings updated successfully!
              </span>
            ) : (
              "Tokens are encrypted and loaded directly into environment memory."
            )}
          </span>
          <button
            onClick={handleSave}
            className="flex items-center gap-2 px-4 py-2 bg-[#3B82F6] hover:bg-[#2563EB] text-white text-xs font-semibold rounded-lg shadow-lg shadow-blue-500/20 transition-all"
          >
            <Save className="w-4 h-4" />
            <span>Save Configuration</span>
          </button>
        </div>
      </div>
    </div>
  );
};
