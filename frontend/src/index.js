import React from 'react';
import ReactDOM from 'react-dom';
import './index.scss';
import App from './App';
import reportWebVitals from './reportWebVitals';

import Home from "./routes/home/home";

import {BrowserRouter, Routes, Route, Navigate} from "react-router-dom";
import AudioStream from "./routes/audiostream/audiostream";


ReactDOM.render(
	<React.StrictMode>
		<BrowserRouter>
			<Routes>
				<Route path="/" element={<App/>}>
					<Route path="audio-stream" 	element={<AudioStream/>}/>
					<Route path="auxiliary" 	element={<Home mode="AUXILIARY"/>} />
					<Route index 				element={<Home mode="MAIN"/>} />
					<Route path='*' element={<Navigate replace to="/" />} />
				</Route>
			</Routes>
		</BrowserRouter>,
	</React.StrictMode>,
	document.getElementById('root')
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
