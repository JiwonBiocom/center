import { useState } from 'react'
import PackageModal from '../components/PackageModal'
import PackageHeader from '../components/packages/PackageHeader'
import PackageGrid from '../components/packages/PackageGrid'
import { usePackages } from '../hooks/usePackages'

interface PackageType {
  package_id: number
  package_name: string
  total_sessions: number
  price: number
  valid_days: number
  is_active: boolean
  description?: string
  created_at?: string
}

export default function Packages() {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingPackage, setEditingPackage] = useState<PackageType | null>(null)
  
  const {
    packages,
    loading,
    showInactive,
    setShowInactive,
    fetchPackages,
    handleToggleActive
  } = usePackages()

  const handleEdit = (pkg: PackageType) => {
    setEditingPackage(pkg)
    setIsModalOpen(true)
  }

  return (
    <div className="p-8">
      <PackageHeader
        showInactive={showInactive}
        onShowInactiveChange={setShowInactive}
        onAddPackage={() => {
          setEditingPackage(null)
          setIsModalOpen(true)
        }}
      />

      <PackageGrid
        packages={packages}
        loading={loading}
        onEdit={handleEdit}
        onToggleActive={handleToggleActive}
      />

      <PackageModal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false)
          setEditingPackage(null)
        }}
        onSuccess={() => {
          setIsModalOpen(false)
          setEditingPackage(null)
          fetchPackages()
        }}
        packageData={editingPackage}
      />
    </div>
  )
}