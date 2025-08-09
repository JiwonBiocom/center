export const SERVICE_COLORS = {
  '브레인': {
    bg: 'bg-blue-100 text-blue-800',
    text: 'text-blue-600',
    border: 'border-blue-300'
  },
  '펄스': {
    bg: 'bg-green-100 text-green-800',
    text: 'text-green-600',
    border: 'border-green-300'
  },
  '림프': {
    bg: 'bg-purple-100 text-purple-800',
    text: 'text-purple-600',
    border: 'border-purple-300'
  },
  '레드': {
    bg: 'bg-red-100 text-red-800',
    text: 'text-red-600',
    border: 'border-red-300'
  },
  '하이드로': {
    bg: 'bg-cyan-100 text-cyan-800',
    text: 'text-cyan-600',
    border: 'border-cyan-300'
  }
};

const DEFAULT_COLORS = {
  bg: 'bg-gray-100 text-gray-800',
  text: 'text-gray-600',
  border: 'border-gray-300'
};

export function getServiceColor(serviceName: string, type: 'bg' | 'text' | 'border' = 'bg'): string {
  return SERVICE_COLORS[serviceName as keyof typeof SERVICE_COLORS]?.[type] || DEFAULT_COLORS[type];
}

export const SERVICE_TYPES = Object.keys(SERVICE_COLORS);