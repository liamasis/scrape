import './App.scss';

import React from 'react';
import Button from 'react-bootstrap/Button';
import Navbar from 'react-bootstrap/Navbar'
import Container from 'react-bootstrap/Container'

import Form from 'react-bootstrap/Form';

import {Link, Outlet} from "react-router-dom";

import {Nav} from "react-bootstrap";

const axios = require('axios').default;

class App extends React.Component {

	static NAME = 'SCRAPE_ELEGY'
	static SERVER_PORT = 8000

	render() {
		return (
			<div className="App">
				<Outlet/>
			</div>
		)
	}
}

export default App;
