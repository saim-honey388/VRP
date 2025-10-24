import { useState, useEffect } from 'react'
import './App.css'

// Type definitions
interface OptimizationResult {
  id: string
  status: string
  progress: number
  currentGeneration: number
  bestFitness: number
  totalCost: number
  totalDistance: number
  routes: Array<{
    id: string
    vehicleId: string
    vehicleType: string
    stops: Array<{
      id: string
      name: string
      lat: number
      lng: number
      type: string
      demand: number
      arrivalTime: string
      serviceTime: number
    }>
    totalDistance: number
    totalTime: number
    totalCost: number
    capacity: number
    violations: string[]
  }>
  violations: Array<{
    depotId: string
    remainingDemand: number
    status: string
  }>
  logs: Array<{
    timestamp: string
    level: string
    message: string
  }>
}

// Professional VRP Optimizer with Bootstrap and Vibrant Colors
function App() {
  const [currentPage, setCurrentPage] = useState('dashboard')
  // Global factory + depots used across pages
  const [factoryGlobal, setFactoryGlobal] = useState<{lat: number, lng: number, name: string} | null>(null)
  const [locations, setLocations] = useState<Array<{ id: string, name: string, lat: number, lng: number, type: 'depot', demand: number }>>([])
  // Start with no vehicles; user adds them
  const [vehicles, setVehicles] = useState<Array<{ id: string, name: string, capacity: number, costPerKm: number, count: number, type: 'owned' | 'rented', fixedRentalCost?: number }>>([])
  const [optimizationResult, setOptimizationResult] = useState<OptimizationResult | null>(null)
  const [isOptimizing, setIsOptimizing] = useState(false)
  const [apiStatus, setApiStatus] = useState('checking')

  // Check API status on load
  useEffect(() => {
    checkAPIStatus()
  }, [])

  const checkAPIStatus = async () => {
    try {
      const response = await fetch('http://localhost:8000/')
      await response.json()
      setApiStatus('connected')
    } catch (error) {
      setApiStatus('disconnected')
    }
  }

  const Navigation = () => (
    <nav className="navbar navbar-expand-lg navbar-custom">
      <div className="container-fluid">
        <div className="navbar-brand d-flex align-items-center text-white">
          <div className="me-3">
            <span className="fs-1">🚛</span>
          </div>
      <div>
            <h4 className="mb-0 fw-bold">VRP Optimizer</h4>
            <small className="opacity-75">Vehicle Routing Solution</small>
      </div>
        </div>
        
        <div className="navbar-nav ms-auto">
          {[
            { name: 'Dashboard', page: 'dashboard', icon: '📊', color: 'btn-primary-custom' },
            { name: 'Map Picker', page: 'map', icon: '🗺️', color: 'btn-success-custom' },
            { name: 'Fleet', page: 'vehicles', icon: '🚛', color: 'btn-warning-custom' },
            { name: 'Optimize', page: 'optimize', icon: '⚡', color: 'btn-info-custom' },
            { name: 'Results', page: 'results', icon: '📈', color: 'btn-custom' }
          ].map((item) => (
            <button
              key={item.name}
              onClick={() => setCurrentPage(item.page)}
              className={`btn ${item.color} me-2 ${currentPage === item.page ? 'active' : ''}`}
            >
              <span className="me-2">{item.icon}</span>
              {item.name}
        </button>
          ))}
        </div>
      </div>
    </nav>
  )

  const Dashboard = () => (
    <div className="container-fluid py-4">
      <div className="row mb-4">
        <div className="col-12">
          <h1 className="display-4 fw-bold text-white text-center mb-3">
            🚛 VRP Optimizer Dashboard
          </h1>
          <p className="lead text-white text-center">Professional Vehicle Routing Problem Optimization System</p>
        </div>
      </div>

      {/* API Status */}
      <div className="row mb-4">
        <div className="col-12">
          <div className={`card card-custom ${apiStatus === 'connected' ? 'border-success' : apiStatus === 'disconnected' ? 'border-danger' : 'border-warning'}`}>
            <div className="card-body">
              <div className="d-flex align-items-center">
                <div className={`me-3 ${apiStatus === 'connected' ? 'text-success' : apiStatus === 'disconnected' ? 'text-danger' : 'text-warning'}`}>
                  <span className="fs-1">
                    {apiStatus === 'connected' ? '✅' : apiStatus === 'disconnected' ? '❌' : '🔄'}
                  </span>
                </div>
                <div>
                  <h3 className="card-title">
                    {apiStatus === 'connected' ? 'API Connected' : 
                     apiStatus === 'disconnected' ? 'API Disconnected' : 
                     'Checking API Status...'}
                  </h3>
                  <p className="card-text">
                    {apiStatus === 'connected' ? 'Backend optimization engine is ready' : 
                     apiStatus === 'disconnected' ? 'Please start the backend server' : 
                     'Connecting to optimization engine...'}
        </p>
      </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="row mb-4">
        <div className="col-lg-3 col-md-6 mb-3">
          <div className="stats-card text-center">
            <div className="fs-1 mb-3">📍</div>
            <h3 className="display-4 fw-bold">{locations.length}</h3>
            <p className="fs-5 mb-0">Total Locations</p>
            <small>Active depots</small>
          </div>
        </div>
        
        <div className="col-lg-3 col-md-6 mb-3">
          <div className="stats-card text-center" style={{background: 'linear-gradient(135deg, #00b894 0%, #00a085 100%)'}}>
            <div className="fs-1 mb-3">🚛</div>
            <h3 className="display-4 fw-bold">{vehicles.reduce((sum, v) => sum + v.count, 0)}</h3>
            <p className="fs-5 mb-0">Total Vehicles</p>
            <small>Fleet size</small>
          </div>
        </div>
        
        <div className="col-lg-3 col-md-6 mb-3">
          <div className="stats-card text-center" style={{background: 'linear-gradient(135deg, #e17055 0%, #d63031 100%)'}}>
            <div className="fs-1 mb-3">👥</div>
            <h3 className="display-4 fw-bold">{locations.reduce((sum, l) => sum + l.demand, 0)}</h3>
            <p className="fs-5 mb-0">Total Demand</p>
            <small>Passengers</small>
          </div>
        </div>
        
        <div className="col-lg-3 col-md-6 mb-3">
          <div className="stats-card text-center" style={{background: 'linear-gradient(135deg, #fdcb6e 0%, #e17055 100%)'}}>
            <div className="fs-1 mb-3">{isOptimizing ? '⚡' : '✅'}</div>
            <h3 className="display-4 fw-bold">{isOptimizing ? 'Running...' : 'Ready'}</h3>
            <p className="fs-5 mb-0">Status</p>
            <small>Optimization</small>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="row">
        <div className="col-lg-6 mb-4">
          <div className="card card-custom h-100">
            <div className="card-body">
              <h3 className="card-title d-flex align-items-center">
                <span className="me-3 fs-1">⚡</span> Quick Actions
              </h3>
              <div className="row g-3">
                <div className="col-6">
                  <button 
                    onClick={() => setCurrentPage('map')}
                    className="btn btn-success-custom w-100 py-3"
                  >
                    <div className="fs-2 mb-2">🗺️</div>
                    <div className="fw-bold">Map Picker</div>
                    <small>Set locations</small>
                  </button>
                </div>
                <div className="col-6">
                  <button 
                    onClick={() => setCurrentPage('vehicles')}
                    className="btn btn-warning-custom w-100 py-3"
                  >
                    <div className="fs-2 mb-2">🚛</div>
                    <div className="fw-bold">Fleet</div>
                    <small>Manage vehicles</small>
                  </button>
                </div>
                <div className="col-6">
                  <button 
                    onClick={() => setCurrentPage('optimize')}
                    className="btn btn-info-custom w-100 py-3"
                  >
                    <div className="fs-2 mb-2">⚡</div>
                    <div className="fw-bold">Optimize</div>
                    <small>Run algorithm</small>
                  </button>
                </div>
                <div className="col-6">
                  <button 
                    onClick={() => setCurrentPage('results')}
                    className="btn btn-custom w-100 py-3"
                  >
                    <div className="fs-2 mb-2">📈</div>
                    <div className="fw-bold">Results</div>
                    <small>View analysis</small>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="col-lg-6 mb-4">
          <div className="card card-custom h-100">
            <div className="card-body">
              <h3 className="card-title d-flex align-items-center">
                <span className="me-3 fs-1">📍</span> Current Locations
              </h3>
              <div className="mb-3">
                {locations.map((location) => (
                  <div key={location.id} className="alert alert-info d-flex justify-content-between align-items-center mb-2">
                    <div className="d-flex align-items-center">
                      <div className="bg-primary rounded-circle me-3" style={{width: '12px', height: '12px'}}></div>
                      <div>
                        <strong>{location.name}</strong>
                        <br />
                        <small>{location.demand} passengers</small>
                      </div>
                    </div>
                    <span className="badge bg-primary">{location.type}</span>
                  </div>
                ))}
                {locations.length === 0 && (
                  <div className="text-center py-4">
                    <div className="fs-1 mb-2">📍</div>
                    <p className="text-muted">No locations added yet</p>
                  </div>
                )}
              </div>
              
              {/* Factory summary */}
              <div className="alert alert-success">
                <div className="d-flex align-items-center mb-2">
                  <div className="bg-success rounded-circle me-2" style={{width: '8px', height: '8px'}}></div>
                  <strong>Factory</strong>
                </div>
                {factoryGlobal ? (
                  <p className="mb-0">{factoryGlobal.name} @ {factoryGlobal.lat.toFixed(4)}, {factoryGlobal.lng.toFixed(4)}</p>
                ) : (
                  <p className="mb-0">Not set. Go to Map Picker.</p>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )

  const MapPicker = () => {
    const [mapLoaded, setMapLoaded] = useState(false)
    const [factory, setFactory] = useState<{lat: number, lng: number, name: string} | null>(null)
    const [depots, setDepots] = useState<Array<{id: string, name: string, lat: number, lng: number, demand: number}>>([])
    const [newDepot, setNewDepot] = useState({ name: '', demand: 0 })
    const [searchQuery, setSearchQuery] = useState('')
    const [factoryCoords, setFactoryCoords] = useState({ lat: '', lng: '' })
    const [factoryName, setFactoryName] = useState('')

    useEffect(() => {
      const loadLeaflet = async () => {
        if (!document.querySelector('link[href*="leaflet"]')) {
          const link = document.createElement('link')
          link.rel = 'stylesheet'
          link.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css'
          document.head.appendChild(link)
        }

        if (!(window as any).L) {
          const script = document.createElement('script')
          script.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js'
          script.onload = () => {
            initializeMap()
            setMapLoaded(true)
          }
          document.head.appendChild(script)
        } else {
          initializeMap()
          setMapLoaded(true)
        }
      }

      loadLeaflet()
    }, [])

    const initializeMap = () => {
      const L = (window as any).L
      if (!L) return

      const map = L.map('map-container', { scrollWheelZoom: true }).setView([25.1, 55.17], 11)
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 20 }).addTo(map)

      ;(window as any).vrpMap = map

      map.on('click', (e: any) => {
        const lat = e.latlng.lat
        const lng = e.latlng.lng
        setFactoryCoords({ lat: lat.toFixed(6), lng: lng.toFixed(6) })
      })
    }

    const confirmFactory = () => {
      if (!factoryCoords.lat || !factoryCoords.lng) {
        alert('Please enter coordinates or click on map')
        return
      }
      if (!factoryName.trim()) {
        alert('Please enter a factory name')
        return
      }
      setFactory({
        lat: parseFloat(factoryCoords.lat),
        lng: parseFloat(factoryCoords.lng),
        name: factoryName.trim()
      })
    }

    const addDepot = () => {
      if (!newDepot.name || newDepot.demand <= 0) {
        alert('Please enter depot name and demand')
        return
      }
      if (!factoryCoords.lat || !factoryCoords.lng) {
        alert('Please enter coordinates or click on map')
        return
      }
      
      const depot = {
        id: `D${depots.length + 1}`,
        name: newDepot.name,
        lat: parseFloat(factoryCoords.lat),
        lng: parseFloat(factoryCoords.lng),
        demand: newDepot.demand
      }
      setDepots([...depots, depot])
      setNewDepot({ name: '', demand: 0 })
      setFactoryCoords({ lat: '', lng: '' })
    }

    const searchLocation = async () => {
      if (!searchQuery) {
        alert('Please enter a search query')
        return
      }
      
      console.log('Searching for:', searchQuery)
      
      try {
        const response = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(searchQuery)}&limit=1`)
        console.log('Search response status:', response.status)
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        
        const data = await response.json()
        console.log('Search results:', data)
        
        if (data && data.length > 0) {
          const item = data[0]
          const lat = parseFloat(item.lat)
          const lng = parseFloat(item.lon)
          
          console.log('Found location:', lat, lng)
          
          const map = (window as any).vrpMap
          if (map) {
            map.setView([lat, lng], 13)
            setFactoryCoords({ lat: lat.toFixed(6), lng: lng.toFixed(6) })
            console.log('Map updated to:', lat, lng)
          } else {
            console.error('Map not found')
          }
        } else {
          alert('No results found for: ' + searchQuery)
        }
      } catch (error) {
        console.error('Search failed:', error)
        alert('Search failed: ' + (error instanceof Error ? error.message : 'Unknown error'))
      }
    }

    const confirmAll = () => {
      if (!factory) {
        alert('Please confirm factory first')
        return
      }
      if (depots.length === 0) {
        alert('Please add at least one depot')
        return
      }
      // Save globally but stay on current page
      setFactoryGlobal(factory)
      // Normalize to locations list used across app (type fixed as 'depot')
      setLocations(depots.map(d => ({ ...d, type: 'depot' })))
      alert('Factory and depots saved successfully! You can now navigate to other pages using the navigation bar.')
    }

    return (
      <div className="container-fluid py-4">
        <div className="row mb-4">
          <div className="col-12">
            <h1 className="display-4 fw-bold text-white text-center mb-3">
              🗺️ Interactive Map Picker
            </h1>
            <p className="lead text-white text-center">Set factory and depot locations with precision</p>
          </div>
        </div>

        <div className="row">
          {/* Map Container */}
          <div className="col-lg-8 mb-4">
            <div className="card card-custom">
              <div className="card-header d-flex justify-content-between align-items-center">
                <h3 className="card-title mb-0">Interactive Map</h3>
                <button
                  onClick={() => {setFactory(null); setDepots([])}}
                  className="btn btn-danger"
                >
                  Clear All
                </button>
              </div>
              
              <div className="card-body">
                {/* Search */}
                <div className="row mb-3">
                  <div className="col-9">
                    <input
                      type="text"
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && searchLocation()}
                      placeholder="Search location (e.g., New York, Lahore)"
                      className="form-control form-control-custom"
                    />
                  </div>
                  <div className="col-3">
                    <button
                      onClick={searchLocation}
                      className="btn btn-success-custom w-100"
                    >
                      Search
                    </button>
                  </div>
                </div>

                {/* Map */}
                <div 
                  id="map-container" 
                  className="map-container"
                  style={{ height: '500px' }}
                >
                  {!mapLoaded && (
                    <div className="d-flex align-items-center justify-content-center h-100 bg-light">
                      <div className="text-center">
                        <div className="fs-1 mb-3">🗺️</div>
                        <p className="text-muted fs-5">Loading map...</p>
                      </div>
                    </div>
                  )}
                </div>

                <div className="alert alert-info mt-3">
                  <strong>Instructions:</strong>
                  <ul className="mb-0 mt-2">
                    <li>Search for a location or click on map to get coordinates</li>
                    <li>Set factory location first using the form below</li>
                    <li>Then add depot locations with names and demand</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>

          {/* Controls */}
          <div className="col-lg-4">
            <div className="row">
              {/* Factory Section */}
              <div className="col-12 mb-4">
                <div className="card card-custom">
                  <div className="card-header">
                    <h3 className="card-title d-flex align-items-center mb-0">
                      <span className="me-2 fs-3">🏭</span> Factory Location
                    </h3>
                  </div>
                  
                  <div className="card-body">
                    {factory ? (
                      <div className="alert alert-success">
                        <div className="d-flex align-items-center mb-2">
                          <div className="bg-success rounded-circle me-2" style={{width: '8px', height: '8px'}}></div>
                          <strong>Factory Set</strong>
                        </div>
                        <p className="mb-1">Coordinates: {factory.lat.toFixed(6)}, {factory.lng.toFixed(6)}</p>
                        <p className="mb-0">Name: {factory.name}</p>
                      </div>
                    ) : (
                      <div>
                        <div className="mb-3">
                          <label className="form-label">Factory Name</label>
                          <input
                            type="text"
                            value={factoryName}
                            onChange={(e) => setFactoryName(e.target.value)}
                            className="form-control form-control-custom"
                            placeholder="e.g., Main Factory, Production Plant"
                          />
                        </div>
                        <div className="mb-3">
                          <label className="form-label">Latitude</label>
                          <input
                            type="number"
                            step="0.000001"
                            value={factoryCoords.lat}
                            onChange={(e) => setFactoryCoords({...factoryCoords, lat: e.target.value})}
                            className="form-control form-control-custom"
                            placeholder="25.123456"
                          />
                        </div>
                        <div className="mb-3">
                          <label className="form-label">Longitude</label>
                          <input
                            type="number"
                            step="0.000001"
                            value={factoryCoords.lng}
                            onChange={(e) => setFactoryCoords({...factoryCoords, lng: e.target.value})}
                            className="form-control form-control-custom"
                            placeholder="55.123456"
                          />
                        </div>
                        <button
                          onClick={confirmFactory}
                          className="btn btn-success-custom w-100"
                        >
                          Confirm Factory
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Depot Section */}
              <div className="col-12 mb-4">
                <div className="card card-custom">
                  <div className="card-header">
                    <h3 className="card-title d-flex align-items-center mb-0">
                      <span className="me-2 fs-3">📍</span> Add Depot
                    </h3>
                  </div>
                  
                  <div className="card-body">
                    <div className="mb-3">
                      <label className="form-label">Depot Name</label>
                      <input
                        type="text"
                        value={newDepot.name}
                        onChange={(e) => setNewDepot({...newDepot, name: e.target.value})}
                        className="form-control form-control-custom"
                        placeholder="e.g., Central Depot"
                      />
                    </div>
                    <div className="mb-3">
                      <label className="form-label">Demand (Passengers)</label>
                      <input
                        type="number"
                        value={newDepot.demand}
                        onChange={(e) => setNewDepot({...newDepot, demand: parseInt(e.target.value) || 0})}
                        className="form-control form-control-custom"
                        placeholder="50"
                      />
                    </div>
                    <div className="row mb-3">
                      <div className="col-6">
                        <label className="form-label">Latitude</label>
                        <input
                          type="number"
                          step="0.000001"
                          value={factoryCoords.lat}
                          onChange={(e) => setFactoryCoords({...factoryCoords, lat: e.target.value})}
                          className="form-control form-control-custom"
                          placeholder="25.123456"
                        />
                      </div>
                      <div className="col-6">
                        <label className="form-label">Longitude</label>
                        <input
                          type="number"
                          step="0.000001"
                          value={factoryCoords.lng}
                          onChange={(e) => setFactoryCoords({...factoryCoords, lng: e.target.value})}
                          className="form-control form-control-custom"
                          placeholder="55.123456"
                        />
                      </div>
                    </div>
                    <button
                      onClick={addDepot}
                      className="btn btn-primary-custom w-100"
                    >
                      Add Depot
                    </button>
                  </div>
                </div>
              </div>

              {/* Depots List */}
              <div className="col-12 mb-4">
                <div className="card card-custom">
                  <div className="card-header">
                    <h3 className="card-title d-flex align-items-center mb-0">
                      <span className="me-2 fs-3">📍</span> Depots ({depots.length})
                    </h3>
                  </div>
                  
                  <div className="card-body" style={{maxHeight: '300px', overflowY: 'auto'}}>
                    {depots.map((depot) => (
                      <div key={depot.id} className="alert alert-info d-flex justify-content-between align-items-start mb-2">
                        <div className="flex-grow-1">
                          <div className="d-flex align-items-center mb-1">
                            <strong>{depot.name}</strong>
                            <span className="badge bg-primary ms-2">{depot.id}</span>
                          </div>
                          <p className="mb-1 small">
                            Location: {depot.lat.toFixed(4)}, {depot.lng.toFixed(4)}
                          </p>
                          <p className="mb-0 small">{depot.demand} passengers</p>
                        </div>
                        <button
                          onClick={() => setDepots(depots.filter(d => d.id !== depot.id))}
                          className="btn btn-sm btn-outline-danger"
                        >
                          ✕
                        </button>
                      </div>
                    ))}
                    {depots.length === 0 && (
                      <div className="text-center py-4">
                        <div className="fs-1 mb-2">📍</div>
                        <p className="text-muted">No depots added yet</p>
                      </div>
                    )}
                  </div>
                  
                  {/* OK button to save globally */}
                  <div className="card-footer">
                    <button
                      onClick={confirmAll}
                      className="btn btn-success-custom w-100"
                    >
                      OK
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  const Vehicles = () => {
    const [newVehicle, setNewVehicle] = useState({
      name: '',
      capacity: '',
      costPerKm: '',
      count: '',
      fixedRentalCost: ''
    })
    const [vehicleTypeFilter, setVehicleTypeFilter] = useState<'owned' | 'rented'>('owned')
    // Derive owned/rented views from global vehicles
    const ownedVehicles = vehicles.filter(v => v.type === 'owned')
    const rentedVehicles = vehicles.filter(v => v.type === 'rented')

    const addVehicle = () => {
      if (!newVehicle.name || !newVehicle.capacity || !newVehicle.costPerKm || !newVehicle.count) return
      
      const vehicle = {
        id: `V${vehicles.length + 1}`,
        name: newVehicle.name,
        capacity: parseInt(newVehicle.capacity),
        costPerKm: parseFloat(newVehicle.costPerKm),
        count: parseInt(newVehicle.count),
        type: vehicleTypeFilter as 'owned' | 'rented',
        fixedRentalCost: vehicleTypeFilter === 'rented' && newVehicle.fixedRentalCost ? parseFloat(newVehicle.fixedRentalCost) : undefined
      }
      
      setVehicles([...vehicles, vehicle])
      
      setNewVehicle({ name: '', capacity: '', costPerKm: '', count: '', fixedRentalCost: '' })
    }

    const removeVehicle = (id: string, _type: 'owned' | 'rented') => {
      setVehicles(vehicles.filter(v => v.id !== id))
    }

    const currentVehicles = vehicleTypeFilter === 'owned' ? ownedVehicles : rentedVehicles

  return (
      <div className="container-fluid py-4">
        <div className="row mb-4">
          <div className="col-12">
            <h1 className="display-4 fw-bold text-white text-center mb-3">
              🚛 Fleet Management
            </h1>
            <p className="lead text-white text-center">Manage your vehicle fleet with precision</p>
          </div>
        </div>

        {/* Vehicle Type Filter */}
        <div className="row mb-4">
          <div className="col-12">
            <div className="card card-custom">
              <div className="card-body">
                <h3 className="card-title">Vehicle Type Filter</h3>
                <div className="btn-group w-100" role="group">
                  <button
                    onClick={() => setVehicleTypeFilter('owned')}
                    className={`btn ${vehicleTypeFilter === 'owned' ? 'btn-success-custom' : 'btn-outline-success'}`}
                  >
                    🚛 Owned Vehicles
                  </button>
                  <button
                    onClick={() => setVehicleTypeFilter('rented')}
                    className={`btn ${vehicleTypeFilter === 'rented' ? 'btn-primary-custom' : 'btn-outline-primary'}`}
                  >
                    🚌 Rented Vehicles
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="row">
          {/* Add Vehicle Form */}
          <div className="col-lg-6 mb-4">
            <div className="card card-custom h-100">
              <div className="card-header">
                <h3 className="card-title d-flex align-items-center mb-0">
                  <span className="me-2 fs-3">➕</span> Add {vehicleTypeFilter === 'owned' ? 'Owned' : 'Rented'} Vehicle
                </h3>
              </div>
              
              <div className="card-body">
                <div className="mb-3">
                  <label className="form-label">Vehicle Name</label>
                  <input
                    type="text"
                    value={newVehicle.name}
                    onChange={(e) => setNewVehicle({...newVehicle, name: e.target.value})}
                    className="form-control form-control-custom"
                    placeholder="e.g., City Bus, Luxury Coach"
                  />
                </div>
                <div className="mb-3">
                  <label className="form-label">Capacity (Passengers)</label>
                  <input
                    type="number"
                    value={newVehicle.capacity}
                    onChange={(e) => setNewVehicle({...newVehicle, capacity: e.target.value})}
                    className="form-control form-control-custom"
                    placeholder="50"
                  />
                </div>
                <div className="mb-3">
                  <label className="form-label">Cost per KM ($)</label>
                  <input
                    type="number"
                    step="0.1"
                    value={newVehicle.costPerKm}
                    onChange={(e) => setNewVehicle({...newVehicle, costPerKm: e.target.value})}
                    className="form-control form-control-custom"
                    placeholder="2.5"
                  />
                </div>
                <div className="mb-3">
                  <label className="form-label">Count (Available)</label>
                  <input
                    type="number"
                    value={newVehicle.count}
                    onChange={(e) => setNewVehicle({...newVehicle, count: e.target.value})}
                    className="form-control form-control-custom"
                    placeholder="3"
                  />
                </div>
                {vehicleTypeFilter === 'rented' && (
                  <div className="mb-3">
                    <label className="form-label">Fixed Rental Cost ($)</label>
                    <input
                      type="number"
                      step="0.1"
                      value={newVehicle.fixedRentalCost}
                      onChange={(e) => setNewVehicle({...newVehicle, fixedRentalCost: e.target.value})}
                      className="form-control form-control-custom"
                      placeholder="50"
                    />
                  </div>
                )}
                <button
                  onClick={addVehicle}
                  className={`btn w-100 ${vehicleTypeFilter === 'owned' ? 'btn-success-custom' : 'btn-primary-custom'}`}
                >
                  Add {vehicleTypeFilter === 'owned' ? 'Owned' : 'Rented'} Vehicle
                </button>
              </div>
            </div>
          </div>

          {/* Vehicles List */}
          <div className="col-lg-6 mb-4">
            <div className="card card-custom h-100">
              <div className="card-header">
                <h3 className="card-title d-flex align-items-center mb-0">
                  <span className="me-2 fs-3">{vehicleTypeFilter === 'owned' ? '🚛' : '🚌'}</span> 
                  {vehicleTypeFilter === 'owned' ? 'Owned' : 'Rented'} Fleet ({currentVehicles.length})
                </h3>
              </div>
              
              <div className="card-body" style={{maxHeight: '400px', overflowY: 'auto'}}>
                {currentVehicles.map((vehicle) => (
                  <div key={vehicle.id} className={`alert ${vehicleTypeFilter === 'owned' ? 'alert-success' : 'alert-info'} mb-3`}>
                    <div className="d-flex justify-content-between align-items-start mb-2">
                      <div className="d-flex align-items-center">
                        <span className="fs-4 me-3">{vehicleTypeFilter === 'owned' ? '🚛' : '🚌'}</span>
      <div>
                          <h5 className="mb-1">{vehicle.name}</h5>
                          <span className="badge bg-secondary">{vehicle.id}</span>
                        </div>
                      </div>
                      <button
                        onClick={() => removeVehicle(vehicle.id, vehicleTypeFilter)}
                        className="btn btn-sm btn-outline-danger"
                      >
                        ✕
                      </button>
                    </div>
                    <div className="row g-2">
                      <div className="col-6">
                        <div className="bg-white p-2 rounded">
                          <small className="text-muted">Capacity:</small>
                          <div className="fw-bold">{vehicle.capacity} seats</div>
                        </div>
                      </div>
                      <div className="col-6">
                        <div className="bg-white p-2 rounded">
                          <small className="text-muted">Cost:</small>
                          <div className="fw-bold">${vehicle.costPerKm}/km</div>
                        </div>
                      </div>
                      <div className="col-6">
                        <div className="bg-white p-2 rounded">
                          <small className="text-muted">Available:</small>
                          <div className="fw-bold">{vehicle.count} units</div>
                        </div>
                      </div>
                      <div className="col-6">
                        <div className="bg-white p-2 rounded">
                          <small className="text-muted">Type:</small>
                          <div className="fw-bold text-capitalize">{vehicle.type}</div>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
                {currentVehicles.length === 0 && (
                  <div className="text-center py-5">
                    <div className="fs-1 mb-3">{vehicleTypeFilter === 'owned' ? '🚛' : '🚌'}</div>
                    <p className="text-muted fs-5">No {vehicleTypeFilter} vehicles yet</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  const Optimize = () => {
    const [settings, setSettings] = useState({
      populationSize: 50,
      generations: 100,
      maxTime: 480,
      useOSRM: false,
      osrmUrl: 'http://router.project-osrm.org'
    })
    const [timeWindows, setTimeWindows] = useState<Array<{id: string, name: string, start: string, end: string, durationMin: number, demandMultiplier: number}>>([
      { id: 'TW1', name: 'Morning', start: '06:00', end: '09:00', durationMin: 60, demandMultiplier: 1.0 }
    ])

    const addTimeWindow = () => {
      const next = `TW${timeWindows.length + 1}`
      setTimeWindows([...timeWindows, { id: next, name: `Shift ${timeWindows.length + 1}`, start: '08:00', end: '10:00', durationMin: 60, demandMultiplier: 1.0 }])
    }
    const updateTimeWindow = (idx: number, field: string, value: any) => {
      const tws = [...timeWindows]
      ;(tws as any)[idx][field] = field === 'durationMin' || field === 'demandMultiplier' ? Number(value) : value
      setTimeWindows(tws)
    }
    const removeTimeWindow = (idx: number) => {
      const tws = [...timeWindows]
      tws.splice(idx, 1)
      setTimeWindows(tws)
    }

    const runOptimization = async () => {
      if (!factoryGlobal) {
        alert('Please set factory location first!')
        return
      }
      if (locations.length === 0) {
        alert('Please add at least one depot first!')
        return
      }
      if (vehicles.length === 0) {
        alert('Please add at least one vehicle type first!')
        return
      }

      setIsOptimizing(true)
      
      // Include factory in locations array
      const allLocations = []
      if (factoryGlobal) {
        allLocations.push({
          id: 'factory',
          name: factoryGlobal.name,
          lat: factoryGlobal.lat,
          lng: factoryGlobal.lng,
          type: 'factory',
          demand: 0
        })
      }
      allLocations.push(...locations)

      const optimizationData = {
        locations: allLocations,
        vehicleTypes: vehicles,
        timeWindows,
        algorithmSettings: {
          populationSize: settings.populationSize,
          generations: settings.generations,
          maxTime: settings.maxTime,
          algorithm: 'genetic'
        },
        constraints: {
          maxRideTime: 60,
          maxCapacity: true,
          timeWindows: true
        }
      }

      try {
        console.log('Sending optimization data:', optimizationData)

        const response = await fetch('http://localhost:8000/optimize', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(optimizationData)
        })

        if (!response.ok) {
          const errorText = await response.text()
          console.error('Backend error response:', errorText)
          throw new Error(`HTTP error! status: ${response.status} - ${errorText}`)
        }

        const kickedOff = await response.json()
        setOptimizationResult(kickedOff)
        setCurrentPage('results')

        // Poll for completion
        const id = kickedOff.id
        const poll = async () => {
          try {
            const r = await fetch(`http://localhost:8000/optimize/${id}`)
            const data = await r.json()
            setOptimizationResult(data)
            if (data.status === 'running') {
              setTimeout(poll, 1000)
            }
          } catch (e) {
            console.error('Polling error:', e)
          }
        }
        poll()
      } catch (error) {
        console.error('Optimization error:', error)
        alert('Optimization failed: ' + (error as Error).message)
      } finally {
        setIsOptimizing(false)
      }
    }

    return (
      <div className="container-fluid py-4">
        <div className="row mb-4">
          <div className="col-12">
            <h1 className="display-4 fw-bold text-white text-center mb-3">
              ⚡ Run Optimization
            </h1>
            <p className="lead text-white text-center">Configure and run the genetic algorithm optimization</p>
          </div>
        </div>

        <div className="row">
          {/* Settings */}
          <div className="col-lg-6 mb-4">
            <div className="card card-custom">
              <div className="card-header">
                <h3 className="card-title">Algorithm Settings</h3>
              </div>
              
              <div className="card-body">
                <div className="mb-3">
                  <label className="form-label">Population Size</label>
                  <input
                    type="number"
                    value={settings.populationSize}
                    onChange={(e) => setSettings({...settings, populationSize: parseInt(e.target.value)})}
                    className="form-control form-control-custom"
                  />
                </div>
                <div className="mb-3">
                  <label className="form-label">Generations</label>
                  <input
                    type="number"
                    value={settings.generations}
                    onChange={(e) => setSettings({...settings, generations: parseInt(e.target.value)})}
                    className="form-control form-control-custom"
                  />
                </div>
                <div className="mb-3">
                  <label className="form-label">Max Time (minutes)</label>
                  <input
                    type="number"
                    value={settings.maxTime}
                    onChange={(e) => setSettings({...settings, maxTime: parseInt(e.target.value)})}
                    className="form-control form-control-custom"
                  />
                </div>
                {/* OSRM is enabled by default in backend; controls hidden */}
              </div>
            </div>
          </div>

          {/* Time Windows */}
          <div className="col-lg-6 mb-4">
            <div className="card card-custom h-100">
              <div className="card-header d-flex justify-content-between align-items-center">
                <h3 className="card-title mb-0">Shifts / Time Windows</h3>
                <button className="btn btn-sm btn-success" onClick={addTimeWindow}>+ Add Shift</button>
              </div>
              <div className="card-body" style={{maxHeight: '400px', overflowY: 'auto'}}>
                {timeWindows.map((tw, idx) => (
                  <div key={tw.id} className="border rounded p-2 mb-3">
                    <div className="row g-2">
                      <div className="col-3">
                        <label className="form-label">ID</label>
                        <input className="form-control form-control-custom" value={tw.id} onChange={e => updateTimeWindow(idx, 'id', e.target.value)} />
                      </div>
                      <div className="col-5">
                        <label className="form-label">Name</label>
                        <input className="form-control form-control-custom" value={tw.name} onChange={e => updateTimeWindow(idx, 'name', e.target.value)} />
                      </div>
                      <div className="col-2">
                        <label className="form-label">Start</label>
                        <input className="form-control form-control-custom" value={tw.start} onChange={e => updateTimeWindow(idx, 'start', e.target.value)} />
                      </div>
                      <div className="col-2">
                        <label className="form-label">End</label>
                        <input className="form-control form-control-custom" value={tw.end} onChange={e => updateTimeWindow(idx, 'end', e.target.value)} />
                      </div>
                      <div className="col-3">
                        <label className="form-label">Duration (min)</label>
                        <input type="number" className="form-control form-control-custom" value={tw.durationMin} onChange={e => updateTimeWindow(idx, 'durationMin', e.target.value)} />
                      </div>
                      <div className="col-3">
                        <label className="form-label">Demand x</label>
                        <input type="number" step="0.1" className="form-control form-control-custom" value={tw.demandMultiplier} onChange={e => updateTimeWindow(idx, 'demandMultiplier', e.target.value)} />
                      </div>
                      <div className="col-3 d-flex align-items-end">
                        <button className="btn btn-sm btn-outline-danger" onClick={() => removeTimeWindow(idx)}>Remove</button>
                      </div>
                    </div>
                  </div>
                ))}
                {timeWindows.length === 0 && (
                  <div className="text-center text-muted py-4">No shifts added</div>
                )}
              </div>
            </div>
          </div>

          {/* Summary */}
          <div className="col-lg-6 mb-4">
            <div className="card card-custom">
              <div className="card-header">
                <h3 className="card-title">Optimization Summary</h3>
              </div>
              
              <div className="card-body">
                <div className="row g-3">
                  <div className="col-6">
                    <div className="alert alert-info text-center">
                      <div className="fs-4 fw-bold">{locations.length}</div>
                      <small>Locations</small>
                    </div>
                  </div>
                  <div className="col-6">
                    <div className="alert alert-success text-center">
                      <div className="fs-4 fw-bold">{locations.reduce((sum, l) => sum + l.demand, 0)}</div>
                      <small>Total Demand</small>
                    </div>
                  </div>
                  <div className="col-6">
                    <div className="alert alert-warning text-center">
                      <div className="fs-4 fw-bold">{vehicles.length}</div>
                      <small>Vehicle Types</small>
                    </div>
                  </div>
                  <div className="col-6">
                    <div className="alert alert-danger text-center">
                      <div className="fs-4 fw-bold">{vehicles.reduce((sum, v) => sum + v.count, 0)}</div>
                      <small>Total Vehicles</small>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Run Button */}
        <div className="row">
          <div className="col-12 text-center">
            <button
              onClick={runOptimization}
              disabled={isOptimizing || locations.length === 0 || vehicles.length === 0}
              className={`btn ${isOptimizing || locations.length === 0 || vehicles.length === 0 ? 'btn-secondary' : 'btn-info-custom'} btn-lg px-5 py-3`}           >
              {isOptimizing ? '🔄 Running Optimization...' : '⚡ Run VRP Optimization'}
        </button>
          </div>
        </div>
      </div>
    )
  }

  // Function to get street names using Photon with minimal retries
  const getStreetName = async (lat: number, lng: number): Promise<string | null> => {
    // Very simple approach with minimal attempts
    const maxRetries = 2
    const baseTimeout = 8000 // 8 seconds timeout
    
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        console.log(`🔄 Photon attempt ${attempt}/${maxRetries} for coordinates: ${lat}, ${lng}`)
        
        // Single Photon URL for simplicity
        const photonUrl = `https://photon.komoot.io/reverse?lat=${lat}&lon=${lng}&limit=3&lang=en`
        
        const controller = new AbortController()
        const timeoutId = setTimeout(() => controller.abort(), baseTimeout)
        
        const response = await fetch(photonUrl, { signal: controller.signal })
        clearTimeout(timeoutId)
        
        if (response.ok) {
          const data = await response.json()
          console.log(`📊 Photon response for attempt ${attempt}:`, data)
          
          if (data.features && data.features.length > 0) {
            // Try to find the best street name from features
            for (const feature of data.features) {
              const properties = feature.properties
              
              // Simple priority order for street names
              const streetName = properties.street || 
                               properties.name || 
                               properties.label
              
              if (streetName && 
                  streetName !== 'Unnamed Road' && 
                  streetName.length > 2 &&
                  !streetName.match(/^\d+$/) && // Not just numbers
                  !streetName.includes('undefined')) {
                console.log(`✅ Photon found real street (attempt ${attempt}):`, streetName)
                return streetName
              }
            }
          }
        }
        
        // Simple delay between retry attempts
        if (attempt < maxRetries) {
          console.log(`⏳ Waiting before retry ${attempt + 1}...`)
          await new Promise(resolve => setTimeout(resolve, 2000))
        }
        
      } catch (error) {
        console.log(`❌ Photon attempt ${attempt} failed:`, error)
        if (attempt === maxRetries) {
          console.log('🚫 All Photon attempts failed')
        }
      }
    }
    
    // If all Photon attempts fail, return null
    return null
  }

  // Function to get road segments between waypoints with minimal complexity
  const getDetailedRoadSegments = async (startLat: number, startLng: number, endLat: number, endLng: number): Promise<string[]> => {
    const roadSegments: string[] = []
    
    try {
      // Very simple approach - just get one intermediate point
      const midLat = (startLat + endLat) / 2
      const midLng = (startLng + endLng) / 2
      
      console.log(`🛣️ Getting road segment at: ${midLat}, ${midLng}`)
      
      const streetName = await getStreetName(midLat, midLng)
      if (streetName) {
        roadSegments.push(streetName)
      }
      
      // Simple delay
      await new Promise(resolve => setTimeout(resolve, 1500))
    } catch (error) {
      console.log('Error getting road segments:', error)
    }
    
    return roadSegments
  }

  // Function to get route steps using real street names
  const getRouteSteps = async (routeCoords: [number, number][], factoryGlobal: any, route: any): Promise<string[]> => {
    const steps: string[] = []
    
    try {
      // Method 1: Try to get real street names with detailed road segments
      if (routeCoords.length > 1) {
        steps.push(`Start at ${factoryGlobal?.name || 'Factory'}`)
        
        // Get detailed road segments for each route leg
        for (let i = 0; i < routeCoords.length - 1; i++) {
          const startCoord = routeCoords[i]
          const endCoord = routeCoords[i + 1]
          
          console.log(`🛣️ Getting detailed roads from ${startCoord} to ${endCoord}`)
          
          // Get detailed road segments between waypoints
          const roadSegments = await getDetailedRoadSegments(
            startCoord[0], startCoord[1], 
            endCoord[0], endCoord[1]
          )
          
          // Add road segments to steps
          roadSegments.forEach((road, index) => {
            if (index === 0) {
              steps.push(`Continue on ${road}`)
            } else {
              steps.push(`Turn onto ${road}`)
            }
          })
          
          // Find the corresponding depot for the end point
          const depot = route.stops.find((stop: any) => 
            Math.abs(stop.lat - endCoord[0]) < 0.001 && Math.abs(stop.lng - endCoord[1]) < 0.001
          )
          
          if (depot) {
            steps.push(`Arrive at ${depot.name} (+${depot.demand} passengers)`)
          }
          
          // Simple delay between route legs
          await new Promise(resolve => setTimeout(resolve, 1000))
        }
        
        // Get return route with detailed segments
        const returnSegments = await getDetailedRoadSegments(
          routeCoords[routeCoords.length - 1][0], routeCoords[routeCoords.length - 1][1],
          routeCoords[0][0], routeCoords[0][1]
        )
        
        returnSegments.forEach((road, index) => {
          if (index === 0) {
            steps.push(`Return via ${road}`)
          } else {
            steps.push(`Continue on ${road}`)
          }
        })
        
        steps.push(`Arrive at ${factoryGlobal?.name || 'Factory'}`)
      }
      
      // Method 2: Try OSRM for detailed instructions (as backup)
      if (steps.length === 0) {
        try {
          const osrmCoords = routeCoords.map(coord => `${coord[1]},${coord[0]}`).join(';')
          const osrmUrl = `http://router.project-osrm.org/route/v1/driving/${osrmCoords}?overview=full&steps=true&geometries=geojson&continue_straight=false`
          
          const osrmResponse = await fetch(osrmUrl)
          if (osrmResponse.ok) {
            const osrmData = await osrmResponse.json()
            console.log('OSRM Response:', osrmData)
            
            if (osrmData.routes && osrmData.routes.length > 0) {
              const routeData = osrmData.routes[0]
              
              if (routeData.legs) {
                routeData.legs.forEach((leg: any) => {
                  if (leg.steps) {
                    leg.steps.forEach((step: any) => {
                      if (step.maneuver && step.maneuver.instruction) {
                        steps.push(step.maneuver.instruction)
                      }
                    })
                  }
                })
              }
            }
          }
        } catch (error) {
          console.log('OSRM failed:', error)
        }
      }
      
      // Method 3: Try OpenRouteService Directions API for turn-by-turn
      if (steps.length === 0) {
        try {
          const orsUrl = `https://api.openrouteservice.org/v2/directions/driving-car?api_key=5b3ce3597851110001cf6248e8b3c8e3b1f6484bb8a344547af8b9ae&start=${routeCoords[0][1]},${routeCoords[0][0]}&end=${routeCoords[routeCoords.length-1][1]},${routeCoords[routeCoords.length-1][0]}&continue_straight=false`
          
          const orsResponse = await fetch(orsUrl)
          if (orsResponse.ok) {
            const orsData = await orsResponse.json()
            console.log('ORS Directions Response:', orsData)
            
            if (orsData.features && orsData.features.length > 0) {
              const feature = orsData.features[0]
              if (feature.properties && feature.properties.segments) {
                feature.properties.segments.forEach((segment: any) => {
                  if (segment.steps) {
                    segment.steps.forEach((step: any) => {
                      if (step.instruction) {
                        steps.push(step.instruction)
                      }
                    })
                  }
                })
              }
            }
          }
        } catch (error) {
          console.log('ORS Directions failed:', error)
        }
      }
      
      // Method 4: Basic route without fake street names
      if (steps.length === 0) {
        steps.push(`Start at ${factoryGlobal?.name || 'Factory'}`)
        
        const pickupStops = route.stops.filter((stop: any) => stop.type === 'pickup')
        pickupStops.forEach((stop: any) => {
          steps.push(`Continue to ${stop.name}`)
          steps.push(`Arrive at ${stop.name} (+${stop.demand} passengers)`)
        })
        
        steps.push(`Return to ${factoryGlobal?.name || 'Factory'}`)
        steps.push(`Arrive at ${factoryGlobal?.name || 'Factory'}`)
      }
      
    } catch (error) {
      console.error('Error getting route steps:', error)
      // Fallback to basic route
      steps.push(`${factoryGlobal?.name || 'Factory'}`)
      route.stops.filter((stop: any) => stop.type === 'pickup').forEach((stop: any) => {
        steps.push(stop.name)
      })
      steps.push(`${factoryGlobal?.name || 'Factory'}`)
    }
    
    return steps
  }

  // Component for individual route visualization with real routing data
  const RouteVisualization = ({ route, routeIndex, factoryGlobal, locations }: any) => {
    const [routeSteps, setRouteSteps] = useState<string[]>([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
      const fetchRouteSteps = async () => {
        if (!route.stops || route.stops.length === 0) {
          setLoading(false)
          return
        }

        try {
          const routeCoords: [number, number][] = []
          
          // Start from factory
          if (factoryGlobal) {
            routeCoords.push([factoryGlobal.lat, factoryGlobal.lng])
          }
          
          // Add depot stops
          route.stops.filter((stop: any) => stop.type === 'pickup').forEach((stop: any) => {
            const depot = locations.find((d: any) => d.name === stop.name)
            if (depot) {
              routeCoords.push([depot.lat, depot.lng])
            }
          })
          
          // Return to factory
          if (factoryGlobal) {
            routeCoords.push([factoryGlobal.lat, factoryGlobal.lng])
          }

          if (routeCoords.length > 1) {
            const steps = await getRouteSteps(routeCoords, factoryGlobal, route)
            setRouteSteps(steps)
          } else {
            // If no valid route coordinates, create basic route
            const basicSteps = [`${factoryGlobal?.name || 'Factory'}`]
            route.stops.filter((stop: any) => stop.type === 'pickup').forEach((stop: any) => {
              basicSteps.push(stop.name)
            })
            basicSteps.push(`${factoryGlobal?.name || 'Factory'}`)
            setRouteSteps(basicSteps)
          }
        } catch (error) {
          console.error('Error fetching route steps:', error)
          // Fallback to basic route
          const basicSteps = [`${factoryGlobal?.name || 'Factory'}`]
          route.stops.filter((stop: any) => stop.type === 'pickup').forEach((stop: any) => {
            basicSteps.push(stop.name)
          })
          basicSteps.push(`${factoryGlobal?.name || 'Factory'}`)
          setRouteSteps(basicSteps)
        }
        
        setLoading(false)
      }

      fetchRouteSteps()
    }, [route, factoryGlobal, locations])

    if (loading) {
      return (
        <div className="mb-4">
          <h6 className="text-primary mb-3">Route {routeIndex + 1}: {route.vehicleId}</h6>
          <div className="text-center">
            <div className="spinner-border spinner-border-sm text-primary" role="status">
              <span className="visually-hidden">Loading route...</span>
            </div>
            <small className="text-muted d-block mt-2">Loading route details...</small>
          </div>
        </div>
      )
    }

    return (
      <div className="mb-4">
        <h6 className="text-primary mb-3">Route {routeIndex + 1}: {route.vehicleId}</h6>
        <div className="route-visualization">
          {routeSteps.map((step, stepIndex) => (
            <div key={stepIndex} className="d-flex align-items-center mb-2">
              {stepIndex === 0 || stepIndex === routeSteps.length - 1 ? (
                <div className="route-circle bg-danger me-2"></div>
              ) : (
                <div className="route-circle bg-success me-2"></div>
              )}
              <small className={stepIndex === 0 || stepIndex === routeSteps.length - 1 ? "text-muted" : "text-success"}>
                {step}
              </small>
              {stepIndex < routeSteps.length - 1 && (
                <div className="route-line me-2 ms-1"></div>
              )}
            </div>
          ))}
        </div>
      </div>
    )
  }

  const Results = () => {
    const [mapLoaded, setMapLoaded] = useState(false)
    const [routeMap, setRouteMap] = useState<any>(null)

    useEffect(() => {
      if (optimizationResult && optimizationResult.routes && optimizationResult.routes.length > 0) {
        const loadLeaflet = async () => {
          if (!document.querySelector('link[href*="leaflet"]')) {
            const link = document.createElement('link')
            link.rel = 'stylesheet'
            link.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css'
            document.head.appendChild(link)
          }

          if (!(window as any).L) {
            const script = document.createElement('script')
            script.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js'
            script.onload = async () => {
              await initializeRouteMap()
              setMapLoaded(true)
            }
            document.head.appendChild(script)
          } else {
            await initializeRouteMap()
            setMapLoaded(true)
          }
        }

        loadLeaflet()
      }
    }, [optimizationResult])

    const initializeRouteMap = async () => {
      const L = (window as any).L
      if (!L || !optimizationResult) return

      // Clear existing map if any
      if (routeMap) {
        routeMap.remove()
      }

      // Create new map
      const map = L.map('route-map-container', { scrollWheelZoom: true })
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 20 }).addTo(map)

      // Get all coordinates to determine map bounds
      const allCoords: [number, number][] = []
      
      // Add factory marker
      if (factoryGlobal) {
        allCoords.push([factoryGlobal.lat, factoryGlobal.lng])
        L.marker([factoryGlobal.lat, factoryGlobal.lng])
          .addTo(map)
          .bindPopup(`<strong>🏭 Factory:</strong> ${factoryGlobal.name}`)
      }

      // Add depot markers
      locations.forEach(depot => {
        allCoords.push([depot.lat, depot.lng])
        L.marker([depot.lat, depot.lng])
          .addTo(map)
          .bindPopup(`<strong>🏢 Depot:</strong> ${depot.name}<br/>Demand: ${depot.demand} passengers`)
      })

      // Draw vehicle routes with different colors using OSRM routing
      const colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F']
      
      for (let routeIndex = 0; routeIndex < optimizationResult.routes.length; routeIndex++) {
        const route = optimizationResult.routes[routeIndex]
        const color = colors[routeIndex % colors.length]
        
        if (route.stops && route.stops.length > 0) {
          const routeCoords: [number, number][] = []
          
          // Start from factory
          if (factoryGlobal) {
            routeCoords.push([factoryGlobal.lat, factoryGlobal.lng])
          }
          
          // Add depot stops
          route.stops.filter((stop: any) => stop.type === 'pickup').forEach((stop: any) => {
            const depot = locations.find((d: any) => d.name === stop.name)
            if (depot) {
              routeCoords.push([depot.lat, depot.lng])
            }
          })
          
          // Return to factory
          if (factoryGlobal) {
            routeCoords.push([factoryGlobal.lat, factoryGlobal.lng])
          }
          
          // Get OSRM route for each segment
          if (routeCoords.length > 1) {
            try {
              const osrmRoute = await getOSRMRoute(routeCoords)
              if (osrmRoute && osrmRoute.length > 0) {
                L.polyline(osrmRoute, {
                  color: color,
                  weight: 4,
                  opacity: 0.8
                }).addTo(map).bindPopup(`
                  <strong>🚌 Route ${routeIndex + 1}</strong><br/>
                  Vehicle: ${route.vehicleId} (${route.vehicleType})<br/>
                  Capacity: ${route.capacity} passengers<br/>
                  Time: ${route.totalTime?.toFixed(0)} min<br/>
                  Cost: $${route.totalCost?.toFixed(2)}
                `)
              } else {
                // Fallback to straight lines if OSRM fails
                L.polyline(routeCoords, {
                  color: color,
                  weight: 4,
                  opacity: 0.8,
                  dashArray: '5, 5'
                }).addTo(map).bindPopup(`
                  <strong>🚌 Route ${routeIndex + 1}</strong><br/>
                  Vehicle: ${route.vehicleId} (${route.vehicleType})<br/>
                  Capacity: ${route.capacity} passengers<br/>
                  Time: ${route.totalTime?.toFixed(0)} min<br/>
                  Cost: $${route.totalCost?.toFixed(2)}<br/>
                  <small>⚠️ Using straight line (OSRM unavailable)</small>
                `)
              }
            } catch (error) {
              console.error('OSRM routing failed:', error)
              // Fallback to straight lines
              L.polyline(routeCoords, {
                color: color,
                weight: 4,
                opacity: 0.8,
                dashArray: '5, 5'
              }).addTo(map).bindPopup(`
                <strong>🚌 Route ${routeIndex + 1}</strong><br/>
                Vehicle: ${route.vehicleId} (${route.vehicleType})<br/>
                Capacity: ${route.capacity} passengers<br/>
                Time: ${route.totalTime?.toFixed(0)} min<br/>
                Cost: $${route.totalCost?.toFixed(2)}<br/>
                <small>⚠️ Using straight line (OSRM unavailable)</small>
              `)
            }
          }
        }
      }

      // Fit map to show all markers
      if (allCoords.length > 0) {
        const group = new L.featureGroup()
        allCoords.forEach(coord => {
          group.addLayer(L.marker(coord))
        })
        map.fitBounds(group.getBounds().pad(0.1))
      }

      setRouteMap(map)
    }

    // Function to get OSRM route coordinates
    const getOSRMRoute = async (coordinates: [number, number][]): Promise<[number, number][]> => {
      if (coordinates.length < 2) return coordinates

      try {
        // Convert coordinates to OSRM format (lng,lat)
        const osrmCoords = coordinates.map(coord => `${coord[1]},${coord[0]}`).join(';')
        const osrmUrl = `http://router.project-osrm.org/route/v1/driving/${osrmCoords}?overview=full&geometries=geojson`
        
        const response = await fetch(osrmUrl)
        if (!response.ok) {
          throw new Error(`OSRM request failed: ${response.status}`)
        }
        
        const data = await response.json()
        
        if (data.routes && data.routes.length > 0) {
          // Extract coordinates from GeoJSON geometry
          const route = data.routes[0]
          if (route.geometry && route.geometry.coordinates) {
            // Convert from [lng, lat] to [lat, lng] format for Leaflet
            return route.geometry.coordinates.map((coord: [number, number]) => [coord[1], coord[0]])
          }
        }
        
        return coordinates // Fallback to original coordinates
      } catch (error) {
        console.error('OSRM routing error:', error)
        return coordinates // Fallback to original coordinates
      }
    }

    return (
      <div className="container-fluid py-4">
        <div className="row mb-4">
          <div className="col-12">
            <h1 className="display-4 fw-bold text-white text-center mb-3">
              📈 Optimization Results
            </h1>
            <p className="lead text-white text-center">View your VRP optimization results</p>
          </div>
        </div>

        {optimizationResult ? (
          <div className="row">
            {/* Section 1: Mapped Routes View */}
            <div className="col-12 mb-4">
              <div className="card card-custom">
                <div className="card-header">
                  <h3 className="card-title">🗺️ Mapped Routes View</h3>
                </div>
                <div className="card-body">
                  <div id="route-map-container" style={{ height: '500px', width: '100%' }}></div>
                  {!mapLoaded && (
                    <div className="text-center py-4">
                      <div className="spinner-border text-primary" role="status">
                        <span className="visually-hidden">Loading map...</span>
                      </div>
                      <p className="mt-2">Loading route visualization...</p>
                    </div>
                  )}
                </div>
              </div>
            </div>

          {/* Section 2: Vehicle Passenger Details */}
          <div className="col-md-8 mb-4">
            <div className="card card-custom h-100">
              <div className="card-header">
                <h3 className="card-title">👥 Vehicle Passenger Details</h3>
              </div>
              <div className="card-body">
                {optimizationResult.routes && optimizationResult.routes.length > 0 ? (
                  <div>
                    {/* Header Row */}
                    <div className="row mb-2 p-2 bg-light rounded">
                      <div className="col-md-1">
                        <strong>Vehicle ID:</strong>
                      </div>
                      <div className="col-md-1">
                        <strong>Vehicle Type:</strong>
                      </div>
                      <div className="col-md-1">
                        <strong>Total Capacity:</strong>
                      </div>
                      <div className="col-md-1">
                        <strong>Served People:</strong>
                      </div>
                      <div className="col-md-1">
                        <strong>Total Time:</strong>
                      </div>
                      <div className="col-md-1">
                        <strong>Total Cost:</strong>
                      </div>
                      <div className="col-md-6">
                        <strong>Depot Visited:</strong>
                      </div>
                    </div>
                    
                    {/* Data Rows */}
                    {optimizationResult.routes.map((route) => (
                      <div key={route.id} className="row mb-2 p-2 border-bottom">
                        <div className="col-md-1">
                          <span className="text-primary">{route.vehicleId}</span>
                        </div>
                        <div className="col-md-1">
                          <span className="text-info">{route.vehicleType}</span>
                        </div>
                        <div className="col-md-1">
                          <span className="text-warning">{route.capacity}</span>
                        </div>
                        <div className="col-md-1">
                          <span className="text-success">
                            {route.stops?.filter(s => s.type === 'pickup').reduce((sum, stop) => sum + (stop.demand || 0), 0) || 0}
                          </span>
                        </div>
                        <div className="col-md-1">
                          <span className="text-warning">{route.totalTime?.toFixed(0)} min</span>
                        </div>
                        <div className="col-md-1">
                          <span className="text-success">${route.totalCost?.toFixed(2)}</span>
                        </div>
                        <div className="col-md-6">
                          <span className="text-muted">
                            {route.stops?.filter(s => s.type === 'pickup').map((stop, stopIndex) => (
                              <span key={stopIndex}>
                                {stop.name} (+{stop.demand})
                                {stopIndex < route.stops.filter(s => s.type === 'pickup').length - 1 && ', '}
                              </span>
                            ))}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-4">
                    <div className="fs-1 mb-3">📭</div>
                    <h5>No Routes Generated</h5>
                    <p className="text-muted">Run optimization to see vehicle passenger details.</p>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Section 3: Route Visualization */}
          <div className="col-md-4 mb-4">
            <div className="card card-custom h-100">
              <div className="card-header">
                <h3 className="card-title">🗺️ Route Visualization</h3>
              </div>
              <div className="card-body">
                {optimizationResult.routes && optimizationResult.routes.length > 0 ? (
                  <div>
                    {optimizationResult.routes.map((route, routeIndex) => (
                      <RouteVisualization 
                        key={route.id} 
                        route={route} 
                        routeIndex={routeIndex}
                        factoryGlobal={factoryGlobal}
                        locations={locations}
                      />
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-4">
                    <div className="fs-1 mb-3">🗺️</div>
                    <h5>No Routes to Visualize</h5>
                    <p className="text-muted">Run optimization to see route visualization.</p>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Section 4: Total Cost & Time (Compact) */}
          <div className="col-12 mb-4">
            <div className="card card-custom">
              <div className="card-header">
                <h3 className="card-title">💰 Total Cost & Time</h3>
              </div>
              <div className="card-body">
                <div className="row text-center">
                  <div className="col-md-4">
                    <div className="fs-3 mb-2">💵</div>
                    <h4 className="text-success">${optimizationResult.totalCost?.toFixed(2) || '0.00'}</h4>
                    <small className="text-muted">Total Cost</small>
                  </div>
                  <div className="col-md-4">
                    <div className="fs-3 mb-2">⏰</div>
                    <h4 className="text-info">{optimizationResult.routes?.reduce((sum, route) => sum + (route.totalTime || 0), 0).toFixed(0) || '0'} min</h4>
                    <small className="text-muted">Total Time</small>
                  </div>
                  <div className="col-md-4">
                    <div className="fs-3 mb-2">📏</div>
                    <h4 className="text-primary">{optimizationResult.totalDistance?.toFixed(1) || '0.0'} km</h4>
                    <small className="text-muted">Total Distance</small>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Section 5: Depot Leftovers */}
          <div className="col-12 mb-4">
            <div className="card card-custom">
              <div className="card-header">
                <h3 className="card-title">📋 Depot Status & Leftover Passengers</h3>
              </div>
              <div className="card-body">
                <div className="row">
                  {optimizationResult.violations && optimizationResult.violations.length > 0 ? (
                    optimizationResult.violations.map((depot, index) => (
                      <div key={index} className="col-md-4 mb-3">
                        <div className={`card ${depot.status === 'fully_served' ? 'border-success' : 'border-warning'}`}>
                          <div className={`card-header ${depot.status === 'fully_served' ? 'bg-success' : 'bg-warning'} text-white`}>
                            <h6 className="mb-0">{depot.depotId}</h6>
                          </div>
                          <div className="card-body text-center">
                            <div className="fs-4 mb-2">
                              {depot.status === 'fully_served' ? '✅' : '⚠️'}
                            </div>
                            <strong>Remaining Demand:</strong><br/>
                            <h4 className={`text-${depot.status === 'fully_served' ? 'success' : 'warning'}`}>
                              {depot.remainingDemand}
                            </h4>
                            <span className={`badge ${depot.status === 'fully_served' ? 'bg-success' : 'bg-warning'}`}>
                              {depot.status === 'fully_served' ? 'Fully Served' : 'Partially Served'}
                            </span>
                          </div>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="col-12 text-center">
                      <div className="fs-1 mb-3">🎉</div>
                      <h4>All Depots Fully Served!</h4>
                      <p className="text-muted">No leftover passengers at any depot.</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="row">
          <div className="col-12">
            <div className="card card-custom text-center">
              <div className="card-body py-5">
                <div className="fs-1 mb-4">📊</div>
                <h3 className="card-title">No Results Yet</h3>
                <p className="card-text text-muted mb-4">Run an optimization to see results here.</p>
                <button
                  onClick={() => setCurrentPage('optimize')}
                  className="btn btn-info-custom btn-lg"
                >
                  Run Optimization
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
  }

  const renderPage = () => {
    switch (currentPage) {
      case 'dashboard': return <Dashboard />
      case 'map': return <MapPicker />
      case 'vehicles': return <Vehicles />
      case 'optimize': return <Optimize />
      case 'results': return <Results />
      default: return <Dashboard />
    }
  }

  return (
    <div>
      <Navigation />
      {renderPage()}
    </div>
  )
}

export default App