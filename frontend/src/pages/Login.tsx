import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { tokenManager } from '../lib/tokenManager'
import { auth } from '../lib/auth'
import { useAuth } from '../contexts/AuthContext'

export default function Login() {
  const navigate = useNavigate()
  const { checkAuth } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const tokens = await auth.login({ email, password })
      tokenManager.handleLogin(tokens.access_token, tokens.refresh_token)
      await checkAuth() // 사용자 정보 다시 가져오기
      navigate('/')
    } catch (error: any) {
      console.error('로그인 에러 상세:', error)
      
      // 에러 메시지 상세 표시
      let errorMessage = '로그인 중 오류가 발생했습니다.\n\n'
      
      if (error.response) {
        errorMessage += `상태 코드: ${error.response.status}\n`
        if (error.response.data?.detail) {
          errorMessage += `서버 메시지: ${error.response.data.detail}\n`
        }
        if (error.response.status === 401) {
          errorMessage += '이메일 또는 비밀번호가 올바르지 않습니다.'
        } else if (error.response.status === 404) {
          errorMessage += 'API 엔드포인트를 찾을 수 없습니다.'
        } else if (error.response.status === 500) {
          errorMessage += '서버 내부 오류가 발생했습니다.'
        }
      } else if (error.request) {
        errorMessage += '서버에 연결할 수 없습니다.\n'
        errorMessage += `API URL: ${import.meta.env.VITE_API_URL}`
      } else {
        errorMessage += `오류: ${error.message}`
      }
      
      setError(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            AIBIO 센터 관리 시스템
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            로그인하여 시작하세요
          </p>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <input type="hidden" name="remember" value="true" />
          <div className="rounded-md shadow-sm -space-y-px">
            <div>
              <label htmlFor="email-address" className="sr-only">
                이메일 주소
              </label>
              <input
                id="email-address"
                name="email"
                type="email"
                autoComplete="email"
                required
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                placeholder="이메일 주소"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
            <div>
              <label htmlFor="password" className="sr-only">
                비밀번호
              </label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="current-password"
                required
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                placeholder="비밀번호"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
          </div>

          {error && (
            <div className="rounded-md bg-red-50 p-4">
              <pre className="text-sm text-red-800 whitespace-pre-wrap font-sans">{error}</pre>
            </div>
          )}

          <div>
            <button
              type="submit"
              disabled={loading}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? '로그인 중...' : '로그인'}
            </button>
          </div>

        </form>
      </div>
    </div>
  )
}