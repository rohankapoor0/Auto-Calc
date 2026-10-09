import React, { useState, useEffect } from 'react'
import { Sidebar, type NavSection } from './components/Sidebar'
import { Header } from './components/Header'
import { VehicleSelector } from './components/VehicleSelector'
import { VehicleComparison } from './components/VehicleComparison'
import { OverviewView } from './views/OverviewView'
import { SpecificationsView } from './views/SpecificationsView'
import { BasicCalculationsView } from './views/BasicCalculationsView'
import { DrivetrainView } from './views/DrivetrainView'
import { RoadResistanceView } from './views/RoadResistanceView'
import { TractionView } from './views/TractionView'
import { ClutchView } from './views/ClutchView'
import { AWDView } from './views/AWDView'
import {
  fetchAllProfiles,
  fetchProfileSpecs,
  calculateVehicle,
} from './services/bridgeService'
import type {
  FullVehicleCalculationResponse,
  VehicleSpecifications,
  VehicleProfile,
} from './types'
import localProfilesData from './data/vehicleProfiles.json'

export const App: React.FC = () => {
  const [activeSection, setActiveSection] = useState<NavSection>('overview')

  // Profile management
  const [profiles, setProfiles] = useState<Record<string, VehicleProfile>>(
    localProfilesData as unknown as Record<string, VehicleProfile>
  )
  const [selectedProfileId, setSelectedProfileId] = useState<string>('hyundai_creta_15_crdi_6mt')

  // Cache of calculation results across vehicles for instant comparison
  const [comparisonCalculations, setComparisonCalculations] = useState<
    Record<string, FullVehicleCalculationResponse | null>
  >({})

  // User-editable specifications for the active vehicle
  const [specs, setSpecs] = useState<VehicleSpecifications | null>(null)
  const [defaultProfileSpecs, setDefaultProfileSpecs] = useState<VehicleSpecifications | null>(null)
  const [metadata, setMetadata] = useState<Record<string, any>>({})
  const [results, setResults] = useState<FullVehicleCalculationResponse | null>(null)

  const [isCalculating, setIsCalculating] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // 1. Load profiles from Python on mount
  useEffect(() => {
    async function initApp() {
      try {
        setIsCalculating(true)
        const profileResp = await fetchAllProfiles()
        if (profileResp?.profiles) {
          setProfiles(profileResp.profiles)
        }
        await loadAndCalculateProfile(selectedProfileId)
      } catch (err: any) {
        console.error('Failed to initialize profiles from Python:', err)
        setError(`Failed to connect to local Python process: ${err.message}`)
      } finally {
        setIsCalculating(false)
      }
    }
    initApp()
  }, [])

  // 2. Load and calculate for a specific vehicle profile
  const loadAndCalculateProfile = async (profileId: string) => {
    try {
      setIsCalculating(true)
      setError(null)

      // Fetch official defaults for this profile from Python adapter
      const profileSpecs = await fetchProfileSpecs(profileId)
      setDefaultProfileSpecs(profileSpecs)
      setSpecs({ ...profileSpecs })

      // Determine AWD eligibility (only Creta has the hypothetical study)
      const isAwdEligible = profileId === 'hyundai_creta_15_crdi_6mt'
      const calcRes = await calculateVehicle(profileSpecs, isAwdEligible)

      setResults(calcRes)
      setMetadata(calcRes.vehicle_specifications || {})

      // Update comparison cache
      setComparisonCalculations(prev => ({
        ...prev,
        [profileId]: calcRes,
      }))
    } catch (err: any) {
      console.error(`Error calculating profile ${profileId}:`, err)
      setError(`Calculation Error: ${err.message}`)
    } finally {
      setIsCalculating(false)
    }
  }

  // 3. Profile selection change handler
  const handleSelectProfile = (newProfileId: string) => {
    if (newProfileId === selectedProfileId) return
    setSelectedProfileId(newProfileId)
    loadAndCalculateProfile(newProfileId)
  }

  // 4. Calculate All with current specs
  const handleCalculateAll = async (targetSpecs?: VehicleSpecifications) => {
    const specsToUse = targetSpecs || specs
    if (!specsToUse) return

    try {
      setIsCalculating(true)
      setError(null)
      const isAwdEligible = selectedProfileId === 'hyundai_creta_15_crdi_6mt'
      const res = await calculateVehicle(specsToUse, isAwdEligible)
      setResults(res)
      setComparisonCalculations(prev => ({
        ...prev,
        [selectedProfileId]: res,
      }))
    } catch (err: any) {
      console.error('Calculation error:', err)
      setError(`Calculation Error: ${err.message}`)
    } finally {
      setIsCalculating(false)
    }
  }

  // 5. Reset to original manufacturer profile defaults
  const handleResetDefaults = () => {
    if (!defaultProfileSpecs) return
    setSpecs({ ...defaultProfileSpecs })
    handleCalculateAll(defaultProfileSpecs)
  }

  const handleChangeSpec = (key: string, value: any) => {
    if (!specs) return
    setSpecs(prev => (prev ? { ...prev, [key]: value } : prev))
  }

  const currentProfile = profiles[selectedProfileId]
  const isAwdSupported = selectedProfileId === 'hyundai_creta_15_crdi_6mt'

  const getSectionTitle = (section: NavSection): string => {
    switch (section) {
      case 'overview':
        return 'Overview Dashboard'
      case 'compare':
        return 'Multi-Vehicle Specification & Performance Comparison'
      case 'basic':
        return 'Basic Vehicle Calculations'
      case 'drivetrain':
        return 'Drivetrain & Speed Performance'
      case 'road_resistance':
        return 'Road Resistance & Power Demand'
      case 'traction':
        return 'FWD Traction & Gradeability'
      case 'clutch':
        return 'Clutch Design & Pressure Distribution'
      case 'awd':
        return 'Hypothetical AWD Analysis'
      case 'specifications':
        return 'Vehicle Engineering Specifications'
    }
  }

  return (
    <div className="app-layout">
      <Sidebar
        activeSection={activeSection}
        onSelectSection={setActiveSection}
        vehicleName={currentProfile ? `${currentProfile.manufacturer} ${currentProfile.name}` : undefined}
        isAwdSupported={isAwdSupported}
      />

      <div className="main-wrapper">
        <Header
          title={getSectionTitle(activeSection)}
          subtitle={
            currentProfile
              ? `${currentProfile.manufacturer} ${currentProfile.name} ${currentProfile.variant} (${currentProfile.fuel_type}, ${currentProfile.transmission})`
              : 'Hyundai Creta 1.5 U2 CRDi Diesel | 6-Speed Manual | FWD'
          }
          isCalculating={isCalculating}
          onCalculateAll={() => handleCalculateAll()}
          onResetDefaults={activeSection === 'specifications' ? handleResetDefaults : undefined}
        />

        {/* Global Vehicle Profile Selector */}
        <VehicleSelector
          profiles={profiles}
          selectedProfileId={selectedProfileId}
          onSelectProfile={handleSelectProfile}
          disabled={isCalculating}
        />

        <main className="content-area">
          {error && (
            <div className="alert-box alert-box-error">
              <strong>Error:</strong> {error}
            </div>
          )}

          {activeSection === 'overview' && (
            <OverviewView
              results={results}
              profile={currentProfile}
              onCalculateAll={() => handleCalculateAll()}
              isCalculating={isCalculating}
              onNavigate={setActiveSection}
            />
          )}

          {activeSection === 'compare' && (
            <VehicleComparison
              profiles={profiles}
              calculations={comparisonCalculations}
              currentProfileId={selectedProfileId}
            />
          )}

          {activeSection === 'specifications' && (
            <SpecificationsView
              specs={specs}
              metadata={metadata}
              currentProfile={currentProfile}
              onChangeSpec={handleChangeSpec}
              onResetDefaults={handleResetDefaults}
              onCalculate={() => handleCalculateAll()}
              isCalculating={isCalculating}
              error={error}
            />
          )}

          {activeSection === 'basic' && (
            <BasicCalculationsView
              data={results?.basic_calculations || null}
              onCalculate={() => handleCalculateAll()}
              isCalculating={isCalculating}
            />
          )}

          {activeSection === 'drivetrain' && (
            <DrivetrainView
              data={results?.drivetrain || null}
              onCalculate={() => handleCalculateAll()}
              isCalculating={isCalculating}
            />
          )}

          {activeSection === 'road_resistance' && (
            <RoadResistanceView
              data={results?.road_resistance || null}
              onCalculate={() => handleCalculateAll()}
              isCalculating={isCalculating}
            />
          )}

          {activeSection === 'traction' && (
            <TractionView
              data={results?.traction || null}
              onCalculate={() => handleCalculateAll()}
              isCalculating={isCalculating}
            />
          )}

          {activeSection === 'clutch' && (
            <ClutchView
              data={results?.clutch || null}
              onCalculate={() => handleCalculateAll()}
              isCalculating={isCalculating}
            />
          )}

          {activeSection === 'awd' && (
            <AWDView
              data={results?.awd_hypothetical || null}
              isSupported={isAwdSupported}
              vehicleName={currentProfile ? `${currentProfile.manufacturer} ${currentProfile.name}` : undefined}
              onCalculateAWD={() => handleCalculateAll()}
              isCalculating={isCalculating}
            />
          )}
        </main>
      </div>
    </div>
  )
}

export default App
