import { access_token } from '$lib/store'
import { get } from 'svelte/store'

const fastapi = (operation, url, params, success_callback, failure_callback) => {
    let method = operation
    let content_type = 'application/json'
    let body = JSON.stringify(params)

    let _url = import.meta.env.VITE_SERVER_URL_REAL_ESTATE + url
    if (method === 'get') {
        _url += "?" + new URLSearchParams(params)
    }

    let options = {
        method: method,
        headers: {
            "Content-Type": content_type,
            "Authorization": "Bearer " + get(access_token)  // access_token 추가
        },
        credentials: 'include',
    }

    if (method !== 'get') {
        options['body'] = body
    }

    fetch(_url, options)
        .then(response => {
            if (response.status === 204) {
                if (success_callback) {
                    success_callback()
                }
                return
            }
            response.json()
                .then(json => {
                    if (response.status >= 200 && response.status < 300) {
                        if (success_callback) {
                            success_callback(json)
                        }
                    } else {
                        if (failure_callback) {
                            failure_callback(json)
                        }
                    }
                })
                .catch(error => {
                    if (failure_callback) {
                        failure_callback(error)
                    }
                })
        })
}

export { fastapi }