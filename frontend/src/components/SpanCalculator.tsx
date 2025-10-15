import React, { useState } from 'react';

interface CableData {
  name: string;
  mass_lin_kg_per_m: number;
  E_MPa: number;
  section_mm2: number;
  alpha_1e6_per_C: number;
  rupture_dan: number;
  diameter_mm: number;
}

interface SpanCalcRequest {
  span_length_m: number;
  delta_h_m: number;
  cable: CableData;
  rho_m: number;
  wind_pressure_daPa?: number;
  angle_topo_grade?: number;
}

interface SpanResult {
  geometry: {
    b_m: number;
    F1_m: number;
    F2_m: number;
    H_m: number;
  };
  tensions: {
    T0_dan: number;
    TA_dan: number;
    TB_dan: number;
  };
  warnings: string[];
  errors: string[];
}

const CABLES_PRESETS: CableData[] = [
  {
    name: 'Aster 570',
    mass_lin_kg_per_m: 1.631,
    E_MPa: 78000,
    section_mm2: 564.6,
    alpha_1e6_per_C: 19.1,
    rupture_dan: 17200,
    diameter_mm: 31.5
  },
  {
    name: 'Pétunia 612',
    mass_lin_kg_per_m: 2.311,
    E_MPa: 63000,
    section_mm2: 612.0,
    alpha_1e6_per_C: 20.5,
    rupture_dan: 19800,
    diameter_mm: 34.8
  },
  {
    name: 'Phlox 228',
    mass_lin_kg_per_m: 0.776,
    E_MPa: 74000,
    section_mm2: 228.0,
    alpha_1e6_per_C: 19.3,
    rupture_dan: 7200,
    diameter_mm: 21.8
  }
];

export default function SpanCalculator() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<SpanResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  // Form state
  const [spanLength, setSpanLength] = useState('500');
  const [deltaH, setDeltaH] = useState('10');
  const [rho, setRho] = useState('2000');
  const [selectedCable, setSelectedCable] = useState<CableData>(CABLES_PRESETS[0]);
  const [windPressure, setWindPressure] = useState('');
  const [angle, setAngle] = useState('');

  const handleCalculate = async () => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const payload: SpanCalcRequest = {
        span_length_m: parseFloat(spanLength),
        delta_h_m: parseFloat(deltaH),
        cable: selectedCable,
        rho_m: parseFloat(rho),
        ...(windPressure && { wind_pressure_daPa: parseFloat(windPressure) }),
        ...(angle && { angle_topo_grade: parseFloat(angle) })
      };

      const response = await fetch('/api/calc/span', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        throw new Error(`Erreur HTTP: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.success) {
        setResult(data.result);
      } else {
        setError('Erreur lors du calcul');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur inconnue');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-lg">
        <div className="bg-blue-600 text-white px-6 py-4 rounded-t-lg">
          <h1 className="text-2xl font-bold">Calculateur de Portée</h1>
          <p className="text-blue-100 text-sm mt-1">Calculs mécaniques selon RTE</p>
        </div>

        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Colonne gauche - Saisies */}
            <div className="space-y-4">
              <h2 className="text-lg font-semibold text-gray-700 border-b pb-2">
                Paramètres de la portée
              </h2>

              {/* Sélection du câble */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Câble
                </label>
                <select
                  value={selectedCable.name}
                  onChange={(e) => {
                    const cable = CABLES_PRESETS.find(c => c.name === e.target.value);
                    if (cable) setSelectedCable(cable);
                  }}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                >
                  {CABLES_PRESETS.map(cable => (
                    <option key={cable.name} value={cable.name}>
                      {cable.name} ({cable.mass_lin_kg_per_m} kg/m)
                    </option>
                  ))}
                </select>
              </div>

              {/* Longueur portée */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Longueur de portée (m)
                </label>
                <input
                  type="number"
                  value={spanLength}
                  onChange={(e) => setSpanLength(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                  step="0.1"
                />
              </div>

              {/* Dénivelé */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Dénivelé (m)
                </label>
                <input
                  type="number"
                  value={deltaH}
                  onChange={(e) => setDeltaH(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                  step="0.1"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Positif si support B plus haut
                </p>
              </div>

              {/* Paramètre ρ */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Paramètre ρ (m)
                </label>
                <input
                  type="number"
                  value={rho}
                  onChange={(e) => setRho(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                  step="1"
                />
              </div>

              {/* Optionnels */}
              <div className="border-t pt-4">
                <h3 className="text-sm font-medium text-gray-700 mb-3">Paramètres optionnels</h3>
                
                <div className="space-y-3">
                  <div>
                    <label className="block text-sm text-gray-600 mb-1">
                      Pression du vent (daPa)
                    </label>
                    <input
                      type="number"
                      value={windPressure}
                      onChange={(e) => setWindPressure(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                      step="0.1"
                      placeholder="Optionnel"
                    />
                  </div>

                  <div>
                    <label className="block text-sm text-gray-600 mb-1">
                      Angle topographique (grades)
                    </label>
                    <input
                      type="number"
                      value={angle}
                      onChange={(e) => setAngle(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                      step="0.1"
                      placeholder="Optionnel"
                    />
                  </div>
                </div>
              </div>

              {/* Bouton calculer */}
              <button
                onClick={handleCalculate}
                disabled={loading}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-4 rounded-md transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                {loading ? 'Calcul en cours...' : 'Calculer'}
              </button>
            </div>

            {/* Colonne droite - Résultats */}
            <div className="space-y-4">
              <h2 className="text-lg font-semibold text-gray-700 border-b pb-2">
                Résultats
              </h2>

              {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
                  <p className="font-medium">Erreur</p>
                  <p className="text-sm">{error}</p>
                </div>
              )}

              {result && (
                <div className="space-y-4">
                  {/* Avertissements */}
                  {result.warnings.length > 0 && (
                    <div className="bg-yellow-50 border border-yellow-200 text-yellow-800 px-4 py-3 rounded">
                      {result.warnings.map((warning, i) => (
                        <p key={i} className="text-sm">{warning}</p>
                      ))}
                    </div>
                  )}

                  {/* Erreurs */}
                  {result.errors.length > 0 && (
                    <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
                      {result.errors.map((err, i) => (
                        <p key={i} className="text-sm font-medium">{err}</p>
                      ))}
                    </div>
                  )}

                  {/* Géométrie */}
                  <div className="bg-gray-50 rounded-lg p-4">
                    <h3 className="font-medium text-gray-700 mb-3">Géométrie</h3>
                    <div className="grid grid-cols-2 gap-3 text-sm">
                      <div>
                        <span className="text-gray-600">Corde (b)</span>
                        <p className="font-semibold text-lg">{result.geometry.b_m.toFixed(2)} m</p>
                      </div>
                      <div>
                        <span className="text-gray-600">Flèche médiane (F1)</span>
                        <p className="font-semibold text-lg">{result.geometry.F1_m.toFixed(2)} m</p>
                      </div>
                      <div>
                        <span className="text-gray-600">Flèche point bas (F2)</span>
                        <p className="font-semibold text-lg">{result.geometry.F2_m.toFixed(2)} m</p>
                      </div>
                      <div>
                        <span className="text-gray-600">Creux total (H)</span>
                        <p className="font-semibold text-lg">{result.geometry.H_m.toFixed(2)} m</p>
                      </div>
                    </div>
                  </div>

                  {/* Tensions */}
                  <div className="bg-blue-50 rounded-lg p-4">
                    <h3 className="font-medium text-gray-700 mb-3">Tensions</h3>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Tension horizontale (T₀)</span>
                        <span className="font-semibold">{result.tensions.T0_dan} daN</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Tension support A (bas)</span>
                        <span className="font-semibold">{result.tensions.TA_dan} daN</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Tension support B (haut)</span>
                        <span className="font-semibold">{result.tensions.TB_dan} daN</span>
                      </div>
                    </div>
                  </div>

                  {/* Infos câble */}
                  <div className="bg-gray-100 rounded-lg p-4">
                    <h3 className="font-medium text-gray-700 mb-2">Câble sélectionné</h3>
                    <p className="text-sm text-gray-600">
                      <strong>{selectedCable.name}</strong><br/>
                      Masse: {selectedCable.mass_lin_kg_per_m} kg/m<br/>
                      Rupture: {selectedCable.rupture_dan} daN<br/>
                      Diamètre: {selectedCable.diameter_mm} mm
                    </p>
                  </div>
                </div>
              )}

              {!result && !error && (
                <div className="text-center text-gray-400 py-12">
                  <svg className="mx-auto h-12 w-12 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                  </svg>
                  <p>Les résultats s'afficheront ici</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
