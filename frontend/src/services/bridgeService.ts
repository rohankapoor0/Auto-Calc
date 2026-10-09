import type {
  FullVehicleCalculationResponse,
  VehicleSpecifications,
  VehicleProfile,
} from '../types'

export interface BridgeDefaultsResponse {
  values: VehicleSpecifications
  metadata: Record<string, any>
}

export interface BridgeProfilesResponse {
  summary: {
    profiles: Array<{
      id: string
      name: string
      variant: string
      model_year: string
      manufacturer: string
      fuel_type: string
      drivetrain: string
      transmission: string
      description: string
      source_reference: string
      source_url: string
      source_type: string
    }>
    default_profile_id: string
  }
  profiles: Record<string, VehicleProfile>
}

/**
 * Invokes the local Python bridge CLI directly through the Vite dev process plugin.
 * No external API, no REST endpoints, no remote server.
 */
export async function invokePythonBridge(
  command: 'get_defaults' | 'get_profiles' | 'get_profile_specs' | 'calculate' | 'calculate_profile',
  payload: Record<string, any> = {}
): Promise<any> {
  const reqBody = {
    command,
    ...payload,
  }

  const response = await fetch('/__bridge_rpc', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(reqBody),
  })

  if (!response.ok) {
    let errText = ''
    try {
      const errJson = await response.json()
      errText = errJson.message || errJson.stderr || JSON.stringify(errJson)
    } catch {
      errText = await response.text()
    }
    throw new Error(`Python Bridge Error (${response.status}): ${errText}`)
  }

  const data = await response.json()
  if (data.status === 'error') {
    throw new Error(`Python Engine Error: ${data.message || 'Unknown error'}`)
  }

  return data.data
}

export async function fetchAllProfiles(): Promise<BridgeProfilesResponse> {
  return await invokePythonBridge('get_profiles')
}

export async function fetchProfileSpecs(profileId: string): Promise<VehicleSpecifications> {
  return await invokePythonBridge('get_profile_specs', { profile_id: profileId })
}

export async function fetchDefaultSpecifications(): Promise<BridgeDefaultsResponse> {
  return await invokePythonBridge('get_defaults')
}

export async function calculateVehicle(
  specs: VehicleSpecifications,
  includeAwd: boolean = false
): Promise<FullVehicleCalculationResponse> {
  return await invokePythonBridge('calculate', {
    specifications: specs,
    include_awd: includeAwd,
  })
}

export async function calculateVehicleProfile(
  profileId: string,
  overrides: Partial<VehicleSpecifications> = {},
  includeAwd: boolean = false
): Promise<FullVehicleCalculationResponse> {
  return await invokePythonBridge('calculate_profile', {
    profile_id: profileId,
    overrides,
    include_awd: includeAwd,
  })
}
