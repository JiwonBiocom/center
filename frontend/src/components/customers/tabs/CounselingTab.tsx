import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Calendar, FileText, Clock, CheckCircle, AlertCircle } from 'lucide-react'
import { api } from '../../../lib/api'

interface CounselingTabProps {
  customerId: number
}

export default function CounselingTab({ customerId }: CounselingTabProps) {
  return (
    <div className="p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">상담 내역</h3>
    </div>
  )
}
