import './audiostream.scss';

import React, {Component} from 'react';
import {w3cwebsocket as W3CWebSocket} from "websocket";
import Button from "react-bootstrap/Button";

import App from "../../App";

import Pizzicato from 'pizzicato'
import {clamp} from "../../utils";

import disconnected from "../../disconnected.mp3";

import canAutoplay from 'can-autoplay'

const SERVER_URL = window.location.hostname + ':' + App.SERVER_PORT
const sleep = (ms) => new Promise(r => setTimeout(r, ms));

class AudioStream extends Component {

	static BASE_VOLUME = 1

	queueRunning = false
	audioQueue = []

	backgroundSound = undefined;
	currentSound = undefined;

	// Will be loaded after button is clicked!
	client = undefined;

	componentDidMount() {
		canAutoplay.audio().then(res => {
			if (res.result) this.reconnect()
		});
	}

	constructor(props) {
		super(props);
		this.state = {
			state: 'unarmed',
			text: ''
		}
	}

	waitAudio = (message) => {
		return new Promise(res => {

			let sound = new Pizzicato.Sound({
				source: 'file',
				// options: { path: `http://${SERVER_URL}${message.url}` }
				options: { path: `${message.url}` }
			}, function() {

				// Configure the sound here
				sound.volume = clamp(AudioStream.BASE_VOLUME * (message.volume !== undefined ? message.volume : 1), 0, 1)

				if (message.reverb){

					let reverb = new Pizzicato.Effects.Reverb({
						time: 0.6,
						decay: 0.8,
						reverse: false,
						mix: 0.6
					});

					sound.addEffect(reverb);
				}

				sound.on('end', () => {
					// Don't disconnect immediately, as an effect may still be playing
					setTimeout(() => {
						sound.disconnect()
					}, 10000)
					res();
				})

				sound.play()
			});


			if (message.background) {
				this.backgroundSound = sound;
			} else {
				this.currentSound = sound;
			}

		})
	}

	runQueue = async () => {
		let message = this.audioQueue.shift()

		if (!message) {
			this.queueRunning = false;
			return;
		}

		console.debug(`Play ${message.url}`)

		this.setState({
			text: message.text || ''
		})

		if (message.type == 'PAUSE') {

			await sleep(message.duration);
			console.log(`Sleeping for ${message.duration}`)

		} else {

			if (message.background) {
				this.waitAudio(message)
			} else {
				await this.waitAudio(message)
			}

		}

		this.setState({ text: '' })

		if (this.audioQueue.length) {
			// Sneakily prefetch the next audio. Browser should cache it for us
			fetch(this.audioQueue[0].url)
			setTimeout(this.runQueue, message.gap !== undefined ? message.gap : 700);
		} else {
			this.queueRunning = false;

			// // A touch hacky...
			// if (message.url == '/static/audio_samples/Scrape190622_Audio3_End.mp3' && this.backgroundSound) {
			// 	setTimeout(() => {
			// 		if (this.backgroundSound) this.backgroundSound.stop();
			// 	}, 5000)
			// }
		}

	}

	processMessage = (messageRaw) => {

		let message = JSON.parse(messageRaw.data)
		console.log(message)

		if (message.type === 'AUDIO' || message.type === 'PAUSE') {

			this.audioQueue.push(message)
			if (!this.queueRunning) {
				this.queueRunning = true;
				this.runQueue()
			}

		} else if (message.type === 'USER_INTERRUPT') {

			this.audioQueue = []

			this.setState({text: '' })

			if (this.backgroundSound) {
				this.backgroundSound.stop();
				this.backgroundSound.disconnect();
			}

			if (this.currentSound) {
				this.currentSound.stop();
				this.currentSound.disconnect();
			}

		}

	}

	reconnect = () => {

		if (this.state.state !== 'unarmed') {
			return;
		}

		this.setState({state: 'connecting'})
		this.client = new W3CWebSocket(`ws://${SERVER_URL}/ws/audio-stream/`);

		this.client.onopen = () => {
			console.log('WebSocket Client Connected');
			this.setState({state: 'connected'})
			// let sound = new Pizzicato.Sound('/static/audio_samples/connected.mp3', () => {
			// 	sound.play()
			// });
		};

		this.client.onmessage = (message) => {
			this.processMessage(message)
		};

		this.client.onerror = (err) => {
			console.log('WEBSOCKET ERROR')
			console.log(err)
		}

		this.client.onclose = (err) => {
			console.log(err)
			if(this.state.state === 'connected') {
				let sound = new Pizzicato.Sound(disconnected, () => {
					sound.play()
				});
			}
			this.setState({ state: 'unarmed' })
            setTimeout(this.reconnect, 10000)
		}
	}

	render() {
		return (
			<div className={`AudioStream ${this.state.state}`}>
				<Button variant="primary" onClick={this.reconnect}>
					Connect
				</Button>
				<div className={`captions ${this.state.text ? 'show' : ''}`}>{this.state.text}</div>
			</div>
		);
	}
}

export default AudioStream;
