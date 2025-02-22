import { access_token, username, userpoints, is_login } from "$lib/store"
import { get } from 'svelte/store'
import { goto } from '$app/navigation';
import qs from "qs"

const fastapi = (operation, url, params, success_callback, failure_callback) => {
    // params = params || {};
    // console.log('params:', params);
    let method = operation;
    let content_type = "application/json";
    let body = JSON.stringify(params);
    let _url = import.meta.env.VITE_API_URL + url;
    // let _url = params?.isImage ? (import.meta.env.VITE_API_URL + url) : (import.meta.env.VITE_API_URL + url);
    // GET 요청의 파라미터 처리 수정
    // console.log('body:', body);

    
    
    if (method === 'login') {
        method = 'post';
        content_type = 'application/x-www-form-urlencoded';
        body = params; // qs는 params 데이터를 'application/x-www-form-urlencoded' 형식으로 변환
    }
    let options = {
        method: method,
        headers: {
            "Content-Type": content_type,
            "Accept": params?.isImage ? 'image/*' : 'application/json',
        }
    };
    // if (method === 'get' && params.key) {
        //     options.headers["X-API-KEY"] = params.key;
        //     delete params.key;
        //     if (Object.keys(params).length > 0) {
            //         _url += "?" + new URLSearchParams(params);
            //     }
            // }
    if (method === 'post' && content_type !== 'application/x-www-form-urlencoded') {
        if (params?.key) {
            options.headers["X-API-KEY"] = params.key;
        }
    }

    if (method === 'get') {
        // console.log('params:', params)
        if (params?.key) {
            options.headers["X-API-KEY"] = params.key;
            delete params.key;
        }
        // params가 존재하고 비어있지 않을 때만 URL에 추가
        if (params && Object.keys(params).length > 0) {
            _url += "?" + new URLSearchParams(params);
        }
        // console.log('get_accno_t0424:', _url)
        // console.log('get_accno_t0424:', options.headers)
    }
    // console.log('body:', body);
    const token = get(access_token);  // 'access_token'이 아닌 'accessToken'
    if (token) {
        // console.log('token:', token);
        options.headers["Authorization"] = "Bearer " + token;
    }
    // console.log(options);
    // 로그인 요청에 대한 처리
    
    
    // DELETE 메서드 처리
    if (method === 'delete') {
        // DELETE 요청의 경우 body를 설정하지 않음
        options.body = undefined; // DELETE 요청에서는 body가 필요하지 않음
    }

    // PUT 메서드 처리
    if (method === 'put') {
        // PUT 요청의 경우 body를 설정
        options.body = body; // PUT 요청에서는 body가 필요함
    }
    
    
    
    // const token = localStorage.getItem('accessToken'); // 'access_token'이 아닌 'accessToken'

    if (method !== 'get') {
        options['body'] = body;
    }

    fetch(_url, options)
        .then(response => {
            if (response.status === 204) {
                if (success_callback) {
                    success_callback();
                }
                return;
            }

            if (params?.isImage) {
                response.blob().then(blob => {
                    if (blob.size > 0) {
                        success_callback(URL.createObjectURL(blob));
                    }
                });
                return;
            }

            response.json()
                .then(json => {
                    if (response.status >= 200 && response.status < 300) {
                        if (success_callback) {
                            success_callback(json);
                        }
                    } else if (response.status === 401) {
                        access_token.set('');
                        username.set('');
                        is_login.set(false);
                        goto('/')
                        // alert("로그인이 필요합니다.");
                        // window.location.href = '/';
                    } else {
                        if (failure_callback) {
                            failure_callback(json);
                        } else {
                            alert(JSON.stringify(json));
                        }
                    }
                })
                .catch(error => {
                    console.log(JSON.stringify(error));
                });
        });
};


export default fastapi


export async function logout() {
    
    try {
        // 로그아웃 API 호출 (필요한 경우)
        const response = await fetch('https://api2410.ebesesk.synology.me/auth/logout', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${get(access_token)}`
            }
        });
        
        if (response.ok) {
            // 로컬 스토리지에서 액세스 토큰 삭제
            access_token.set('');
            username.set('');
            userpoints.set(0);
            is_login.set(false);
            return true; // 성공적으로 로그아웃
        } else {
            console.error('로그아웃 실패:', response.statusText);
            return false; // 로그아웃 실패
        }
    } catch (error) {
        console.error('로그아웃 중 오류 발생:', error);
        return false; // 로그아웃 중 오류
    }
}