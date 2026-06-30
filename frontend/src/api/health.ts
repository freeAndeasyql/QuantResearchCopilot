import {request} from './request'

export const getHealth = () => {
    return request.get('/api/health')
}