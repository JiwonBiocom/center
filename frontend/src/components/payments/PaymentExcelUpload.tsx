import { useState } from 'react'
import { Upload, FileSpreadsheet, X, AlertCircle, CheckCircle } from 'lucide-react'
import { api } from '../../lib/api'

interface PaymentExcelUploadProps {
  isOpen: boolean
  onClose: () => void
  onSuccess: () => void
}

interface UploadResult {
  success: boolean
  message: string
  sheet_name?: string
  total_rows?: number
  success_count?: number
  duplicate_count?: number
  error_count?: number
  errors?: string[]
}

export default function PaymentExcelUpload({ isOpen, onClose, onSuccess }: PaymentExcelUploadProps) {
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [result, setResult] = useState<UploadResult | null>(null)
  const [dragActive, setDragActive] = useState(false)

  if (!isOpen) return null

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0]
      if (droppedFile.name.endsWith('.xlsx') || droppedFile.name.endsWith('.xls')) {
        setFile(droppedFile)
        setResult(null)
      }
    }
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0])
      setResult(null)
    }
  }

  const handleUpload = async () => {
    if (!file) return

    setUploading(true)
    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await api.post('/payments/import/excel', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      setResult(response.data)

      if (response.data.success && response.data.success_count > 0) {
        setTimeout(() => {
          onSuccess()
          handleClose()
        }, 2000)
      }
    } catch (error: any) {
      setResult({
        success: false,
        message: error.response?.data?.detail || '업로드 중 오류가 발생했습니다.',
      })
    } finally {
      setUploading(false)
    }
  }

  const handleClose = () => {
    setFile(null)
    setResult(null)
    onClose()
  }

  return (
    <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold text-gray-900">결제 데이터 엑셀 업로드</h2>
          <button
            onClick={handleClose}
            className="text-gray-400 hover:text-gray-500"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        <div className="mb-6">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
            <div className="flex">
              <AlertCircle className="h-5 w-5 text-blue-600 mt-0.5 mr-2 flex-shrink-0" />
              <div className="text-sm text-blue-800">
                <p className="font-semibold mb-1">업로드 가능한 형식:</p>
                <ul className="list-disc list-inside space-y-1">
                  <li>2025년 AIBIO 결제현황.xlsx와 동일한 형식</li>
                  <li>필수 컬럼: 결제일자, 고객명, 결제금액</li>
                  <li>지원 형식: .xlsx, .xls</li>
                </ul>
              </div>
            </div>
          </div>

          <div
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            className={`border-2 border-dashed rounded-lg p-8 text-center ${
              dragActive ? 'border-indigo-500 bg-indigo-50' : 'border-gray-300'
            }`}
          >
            {!file ? (
              <>
                <FileSpreadsheet className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                <p className="text-sm text-gray-600 mb-2">
                  엑셀 파일을 드래그하여 놓거나 클릭하여 선택하세요
                </p>
                <input
                  type="file"
                  accept=".xlsx,.xls"
                  onChange={handleFileChange}
                  className="hidden"
                  id="file-upload"
                />
                <label
                  htmlFor="file-upload"
                  className="cursor-pointer inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
                >
                  <Upload className="h-4 w-4 mr-2" />
                  파일 선택
                </label>
              </>
            ) : (
              <div>
                <FileSpreadsheet className="mx-auto h-12 w-12 text-green-500 mb-4" />
                <p className="text-sm font-medium text-gray-900 mb-1">{file.name}</p>
                <p className="text-xs text-gray-500 mb-4">
                  {(file.size / 1024).toFixed(1)} KB
                </p>
                <button
                  onClick={() => {
                    setFile(null)
                    setResult(null)
                  }}
                  className="text-sm text-indigo-600 hover:text-indigo-500"
                >
                  다른 파일 선택
                </button>
              </div>
            )}
          </div>
        </div>

        {result && (
          <div className={`mb-6 p-4 rounded-lg ${
            result.success ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'
          }`}>
            <div className="flex items-start">
              {result.success ? (
                <CheckCircle className="h-5 w-5 text-green-600 mt-0.5 mr-2 flex-shrink-0" />
              ) : (
                <AlertCircle className="h-5 w-5 text-red-600 mt-0.5 mr-2 flex-shrink-0" />
              )}
              <div className="flex-1">
                <p className={`text-sm font-medium ${
                  result.success ? 'text-green-800' : 'text-red-800'
                }`}>
                  {result.message}
                </p>

                {result.success && (
                  <div className="mt-2 text-sm text-green-700">
                    <p>• 시트: {result.sheet_name}</p>
                    <p>• 전체 행: {result.total_rows}개</p>
                    <p>• 성공: {result.success_count}개</p>
                    {result.duplicate_count > 0 && (
                      <p>• 중복: {result.duplicate_count}개</p>
                    )}
                    {result.error_count > 0 && (
                      <p>• 실패: {result.error_count}개</p>
                    )}
                  </div>
                )}

                {result.errors && result.errors.length > 0 && (
                  <div className="mt-2">
                    <p className="text-sm font-medium text-red-800 mb-1">오류 내역:</p>
                    <ul className="text-xs text-red-700 space-y-1">
                      {result.errors.map((error, idx) => (
                        <li key={idx}>• {error}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        <div className="flex justify-end space-x-3">
          <button
            onClick={handleClose}
            disabled={uploading}
            className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
          >
            닫기
          </button>
          <button
            onClick={handleUpload}
            disabled={!file || uploading || (result?.success && result?.success_count > 0)}
            className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {uploading ? (
              <>
                <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white inline" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                업로드 중...
              </>
            ) : (
              '업로드'
            )}
          </button>
        </div>
      </div>
    </div>
  )
}
