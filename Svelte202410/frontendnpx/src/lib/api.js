// import qs from "qs"
import { access_token, username, is_login } from "./store"
import { get } from 'svelte/store'
import qs from "qs"

const fastapi = (operation, url, params, success_callback, failure_callback) => {
    let method = operation;
    let content_type = "application/json";
    let body = JSON.stringify(params);

    let _url = params?.isImage ? (import.meta.env.VITE_API_URL + url) : (import.meta.env.VITE_API_URL + url);

    // 로그인 요청에 대한 처리
    if (operation === 'login') {
        method = 'post';
        content_type = 'application/x-www-form-urlencoded';
        body = params; // qs는 params 데이터를 'application/x-www-form-urlencoded' 형식으로 변환
    }

    // GET 요청의 파라미터 처리 수정
    if (method === 'get') {
        const searchParams = new URLSearchParams();
        Object.entries(params).forEach(([key, value]) => {
            if (Array.isArray(value)) {
                value.forEach(item => searchParams.append(key, item));
            } else {
                searchParams.append(key, value);
            }
        });
        _url += "?" + searchParams.toString();
    }

    let options = {
        method: method,
        headers: {
            "Content-Type": content_type,
            "Accept": params?.isImage ? 'image/*' : 'application/json'
        }
    };

    const token = localStorage.getItem('accessToken'); // 'access_token'이 아닌 'accessToken'
    if (token) {
        options.headers["Authorization"] = "Bearer " + token;
    }

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
                        alert("로그인이 필요합니다.");
                        window.location.href = '/';
                    } else {
                        if (failure_callback) {
                            failure_callback(json);
                        } else {
                            alert(JSON.stringify(json));
                        }
                    }
                })
                .catch(error => {
                    alert(JSON.stringify(error));
                });
        });
};


export default fastapi