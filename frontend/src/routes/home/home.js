import Form from "react-bootstrap/Form";
import Button from "react-bootstrap/Button";
import React from "react";
import Modal from 'react-bootstrap/Modal'
import Countdown from "react-countdown";

import {w3cwebsocket as W3CWebSocket} from "websocket";

import App from "../../App";

import splash1 from "../../splash1.jpg";

import "./home.scss"
import {Link} from "react-router-dom";
import {Nav} from "react-bootstrap";
import Container from "react-bootstrap/Container";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";
import InputGroup from "react-bootstrap/InputGroup";
import FormControl from "react-bootstrap/FormControl";

import Start from "../start/start.js"
import {default as axios} from "axios";


import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import {faChevronRight, faChevronLeft, faDeleteLeft} from '@fortawesome/free-solid-svg-icons'



const SERVER_URL = window.location.hostname + ':' + App.SERVER_PORT

class Home extends React.Component {

    // Reset on user interaction or modals open / close or on load
    static OPEN_TIMEOUT = 25000

    // Can't be reset
    static MODAL_TIMEOUT    = 15150
    static MODAL_TIMEOUT_XL = 45150

    // Note there also exist the 120 second timeout - but this is set on the server

    static SERVERLESS = false;
    modalButtons = [];
    modalTimeout = undefined;
    openedTimeout = undefined;

    constructor(props) {
        super(props);
        this.state = {
            openedClass: 'hidden',
            modalOpen: false,
            state: Home.SERVERLESS ? 'ready' : 'unarmed',
            loadingState: false,
            instagramHandle: '',
            serverState: -1,
            enterPrompt: false
            // eta: Date.now() + 1000000
        }
        this.formRef = React.createRef();
        this.touches = 0;
        this.reconnectErrors = 0;
    }

    close = () => {
        this.setState({
            openedClass: 'hidden',
        })
        this.clearHandle();
        document.activeElement.blur()
        this.clearOpenTimeout()
    }

    interruptSession = () => {
        this.client.send(JSON.stringify({
            type: 'USER_INTERRUPT'
        }));

        this.closeModal();
    }

    doneFollow = () => {

        this.client.send(JSON.stringify({
            type: 'FOLLOW_RESP_OK'
        }));

        this.closeModal();
    }

    cancelFollow = () => {

        this.client.send(JSON.stringify({
            type: 'FOLLOW_RESP_DECLINED'
        }));

        this.promptFollowRequestFailed()

    }

    resetState = () => {
        console.log("Reset state")
        this.clearModalTimeout();
        this.clearOpenTimeout();

        this.setState({
            openedClass: 'hidden',
        })

        setTimeout(() => {
            this.setState({
                modalOpen: false,
                loadingState: false,
                enterPrompt: false
            })
            this.clearHandle();
            this.stateChange();
        }, 300)

        setTimeout(() => {
            document.activeElement.blur()
        }, 1500)
    }

    closeModal = () => {
        this.clearModalTimeout();

        if (this.onModalCloseAdditionalHandler) {
            this.onModalCloseAdditionalHandler();
            this.onModalCloseAdditionalHandler = undefined;
        }

        if (!this.state.loadingState && this.state.openedClass === 'open') this.registerOpenTimeout();

        this.setState({
            modalOpen: false
        })
    }

    openModal = (timeoutDuration) => {
        this.clearModalTimeout();
        this.clearOpenTimeout();
        this.setState({
            modalOpen: true
        })

        if (timeoutDuration) {
            this.registerModalTimeout(timeoutDuration)
        }
    }

    startClicked = () => {

        this.modalTitle = 'Consent'

        this.modalBody = (
            <div>
                <p><b>SCRAPE_ELEGY</b> is a private restroom for solo reflection on your internet life. The depths of your insta are about to rise up and your old captions may cause you stress when replayed.</p>
                <p>If it's too much, you can leave at any time.</p>
                <p className="style-2">If you press <b>YES</b> below, you are confirming this is okay with you and giving us permission to scrape your insta. We don't keep any data. Ew.</p>
            </div>
        )

        this.modalButtons = ['PROGRESS-45', 'EXPANDO', 'CONSENT-NO-INSTA', 'CONSENT-CONTINUE'];
        this.modalStatic = false;
        this.closeButton = true;

        this.openModal(Home.MODAL_TIMEOUT_XL)

    }



    consentNoInstagram = () => {

        this.modalTitle = 'No Problem'

        this.modalBody = (
            <div>
                <p>Would you still like to come in and listen to <b>our personal Scrape Elegy?</b></p>
            </div>
        )

        this.modalButtons = ['PROGRESS-15', 'EXPANDO', 'OK-SAD', 'DEMO'];
        this.modalStatic = false;
        this.closeButton = false;

        this.openModal(Home.MODAL_TIMEOUT)
    }


    noInstagramConfirm = () => {

        if(this.state.state !== 'ready') return;

        this.closeModal();
        this.startedLoading()
        let that = this;

        axios.post("/api/scrape-dummy", {}, {withCredentials: false})
            .then((result) => {
                console.log("Hooray!")
            })
            .catch(function (error) {
                that.genericError();
            });

    }

    consentContinue = () => {
        this.closeModal();
        this.open();
    }


    open = () => {
        this.registerOpenTimeout()
        this.setState({
            openedClass: 'open',
        })
    }


    registerModalTimeout = (duration) => {
        this.modalTimeout = setTimeout(this.resetState, duration)
    }

    clearModalTimeout = () => {
        if (this.modalTimeout) {
            clearTimeout(this.modalTimeout);
            this.modalTimeout = undefined;
        }
    }


    registerOpenTimeout = () => {
        this.openedTimeout = setTimeout(this.close, Home.OPEN_TIMEOUT)
    }

    clearOpenTimeout = () => {
        if (this.openedTimeout) {
            clearTimeout(this.openedTimeout);
            this.openedTimeout = undefined;
        }
    }

    componentDidMount = () => {
        if (!Home.SERVERLESS) this.reconnect();
        // this.promptFollowRequest('aaa', 'bbb')
    }

    reconnect = () => {

        this.client = new W3CWebSocket(`ws://${SERVER_URL}/ws/frontend-stream/`);

		this.client.onopen = () => {
			console.log('WebSocket Client Connected');
            // If it took us at least a couple tries to reconnect, it's a good bet the server
            // was updated with a new version. So... refresh the page!
            if (this.reconnectErrors >= 2) {
                this.refresh()
            }
            this.reconnectErrors = 0;
			this.setState({state: 'ready'})
		};

		this.client.onmessage = (message) => {
			this.processMessage(message)
		};

		this.client.onerror = (err) => {
            console.log(err)
			this.setState({ state: 'unarmed' })
		}

		this.client.onclose = (err) => {
            console.log("Socket disconnected")
			console.log(err)
            this.reconnectErrors++;
            console.log(`reconnectErrors at ${this.reconnectErrors}`)
			this.setState({ state: 'unarmed' })
            setTimeout(this.reconnect, 10000)
		}
    }


	processMessage = (messageRaw) => {

		let message = JSON.parse(messageRaw.data)
		console.log(message)

        // Only display errors if we're in main mode (not auxiliary)
		if (message.type === 'ERROR' && this.props.mode === 'MAIN') {

            if (message.error === 'USER_DOES_NOT_EXIST') {
                this.userDoesntExist(message.handle)
            }

            if (message.error === 'USER_NO_MEDIAS') {
                this.userNoMedias(message.handle)
            }

            if (message.error === 'NEED_FOLLOW') {
                this.promptFollowRequest(message.handle, message.fromHandle, message.attempt, message.attemptsMax)
            }

            if (message.error === 'NEED_FOLLOW_FINAL') {
                this.promptFollowRequestFailed()
            }

            if (message.error === 'GENERIC') {
                this.genericError()
            }

            if (message.error === 'INSTAGRAM_BLOCKED_US') {
                this.instagramBlocked()
            }

            if (message.error === 'NO_INTERNET') {
                this.genericError('Server is offline', (
                    <div>
                        <p>Our server appears to be offline.</p>
                        <p>Please try your request again later.</p>
                    </div>
                ), true)
            }

        } else if (message.type === 'STATE_CHANGE') {

		    const prevServerState = this.state.serverState;
		    this.setState({
                serverState: message.state,
                eta: message.eta
		    })

		    // If we currently are in enterPrompt - don't trigger a state change
            if (this.state.enterPrompt) {

            // If we have a request pending - prompt the user to enter
            } else if (this.state.state == 'ready' && this.state.loadingState && message.state == 2) {
		        const timeNow = new Date().getTime()
                if (!this.allowLoading || this.allowLoading <= timeNow) {
                    this.promptPleaseEnter(message.dummy)
                } else {
                    setTimeout(() => {this.promptPleaseEnter(message.dummy)}, this.allowLoading - timeNow)
                }

            // Otherwise we're all good, trigger the state change
            } else {
		        this.stateChange();
            }

        }

	}

	stateChange = () => {
        this.setState((state) => {
            return {
                state: state.serverState == 2 ? 'occupied' : 'ready'
            }
        });
    }

    promptPleaseEnter = (dummy) => {
        this.modalTitle = 'Handle accepted'
        this.modalBody = (
            <div>
                <p>Come through by yourself. Take a seat alone.</p>
                <p><b>Remember:</b> if hearing your past posts is too much, you can leave at any time.</p>
            </div>
        )

        if (dummy) {
            this.modalTitle = 'Scrape Elegy starting'
            this.modalBody = (
                <div>
                    <p>We'll play back <b>our personal Scrape Elegy</b>.</p>
                    <p>Come through by yourself. Take a seat alone.</p>
                </div>
            )
        }

        this.modalButtons = ['PROGRESS-15'];
        this.modalStatic = true;
        this.closeButton = false;

        this.setState({
            loadingState: false,
            enterPrompt: true
        });

        this.openModal(Home.MODAL_TIMEOUT)
    }




    promptFollowRequestFailed = () => {
        this.modalTitle = 'Follow request ignored'
        this.modalBody = (
            <div>
                <p>We couldn't scrape your Instagram account.</p>
            </div>
        )
        this.modalButtons = ['PROGRESS-15', 'EXPANDO', 'OK'];
        this.modalStatic = false;
        this.closeButton = false;

        this.onModalCloseAdditionalHandler = () => {
            this.resetState();
        }

        this.close();
        this.setState({
            loadingState: false
        });

        this.openModal(Home.MODAL_TIMEOUT)

    }


    clearHandle = () => {
        if(this.formRef.current) this.formRef.current.clearHandle();
    }

    promptFollowRequest = (handle, fromHandle, attempt, attemptsMax) => {
        this.modalTitle = 'Accept follow request'
        if (attempt !== 1){
            this.modalTitle += ` (Attempt ${attempt} of ${attemptsMax})`
        }

        this.modalBody = (
            <div>
                <p>Hi <b>@{handle}</b>.</p>
                <p>Please accept the follow request from <b>@{fromHandle}</b>, then tap <b>DONE</b>.</p>
            </div>
        )

        this.modalButtons = ['PROGRESS-120', 'EXPANDO', 'CANCEL-FOLLOW', 'DONE-FOLLOW'];
        this.modalStatic = true;
        this.closeButton = false;

        this.openModal() // Timeout is false as server will auto-timeout after 120 seconds of inactivity
    }

    userNoMedias = (handle) => {
        this.genericError('That user doesn\'t have any posts', (
            <div>
                <p><b>@{handle}</b> doesn't have any posts. Try another handle?</p>
            </div>
        ));
    }

    userDoesntExist = (handle) => {
        this.genericError('That user doesn\'t seem to exist', (
            <div>
                <p>We couldn't find an Instagram account with handle <b>@{handle}</b>. Try another handle?</p>
            </div>
        ));
    }

    instagramBlocked = () => {

        // new Date().getDay() == 5 check for Friday
        let timeHorizon = new Date().getHours() >= 16 ? (new Date().getDay() == 5 ? 'on Monday' : 'tomorrow') : 'later today';

        this.modalTitle = '...Instagram has blocked us 😒'
        this.modalBody = (
            <div>
                <p>It appears there are limits to what Big Tech will allow. We can't access your account right now.</p>
                <p>Please try again {timeHorizon}, or come in and listen to <b>our personal Scrape Elegy</b> now.</p>
            </div>
        )

        this.modalButtons = ['PROGRESS-45', 'EXPANDO', 'OK-SAD', 'DEMO'];
        this.modalStatic = false;
        this.closeButton = false;

        this.setState({
            loadingState: false
        })

        setTimeout(this.close, 200)

        this.openModal(Home.MODAL_TIMEOUT_XL)
    }


    askInterruptSession = () => {

        this.modalTitle = 'Secret menu'
        this.modalBody = (
            <div>
                <p>Reset the experience? This will immediately cancel playback of the current audio.</p>
                <p><b>If you got here accidentally</b>, please tap <b>CANCEL</b>.</p>
            </div>
        )

        this.modalButtons = ['PROGRESS-15', 'EXPANDO', 'SECRET-NO', 'SECRET-YES'];
        this.modalStatic = false;
        this.closeButton = false;

        this.setState({
            loadingState: false
        })

        this.openModal(Home.MODAL_TIMEOUT)
    }

    refresh = () => {
        window.location.reload();
        this.closeModal();
    }

    askRefresh = () => {

        this.modalTitle = 'Refresh the page?'
        this.modalBody = (
            <div>
                <p>If SCRAPE_ELEGY is stuck on this page, refreshing this website may help.</p>
                <p>Note: The website <b>must be refreshed</b> whenever the production react build is updated.</p>
            </div>
        )

        this.modalButtons = ['PROGRESS-15', 'EXPANDO', 'REFRESH-NO', 'REFRESH-YES'];
        this.modalStatic = false;
        this.closeButton = false;

        this.setState({
            loadingState: false
        })

        this.openModal(Home.MODAL_TIMEOUT)
    }

    genericError = (title = 'Oops!', body, close= false) => {

        body = body || (
            <div>
                <p>Sorry, something went wrong.</p>
                <p>Please try your request again later.</p>
            </div>
        )

        this.modalTitle = title
        this.modalBody = body
        this.modalButtons = ['PROGRESS-15', 'EXPANDO', 'OK'];
        this.modalStatic = false;
        this.closeButton = false;

        this.setState({
            loadingState: false
        })

        if (close) setTimeout(this.close, 200)

        this.openModal(Home.MODAL_TIMEOUT)
    }

    finishedLoading = () => {
        this.setState({ loadingState: false })
    }

    startedLoading = () => {
        this.clearOpenTimeout();
        // this.allowLoading = new Date().getTime() + 1000 * 18.3 // 18.3 seconds
        this.setState({ loadingState: true })
    }

    getLifecycleState = () => {
        return this.state.state;
    }

    tap = (e) => {
        if (
            this.touches === 0 ||
            (Math.abs(e.screenX - this.touchX) < 50 && Math.abs(e.screenY - this.touchY) < 50)
        ){
            this.touches++
            this.touchX = e.screenX;
            this.touchY = e.screenY;

            if (this.touchTimeout) clearTimeout(this.touchTimeout)
            this.touchTimeout = setTimeout( () => {
                this.touches = 0;
                this.touchX = undefined;
                this.touchY = undefined;
            }, 350);

            if (this.touches === 3 && this.state.state === 'occupied') {
                this.askInterruptSession()
            }
            if (this.touches === 10 && this.state.state !== 'occupied') {
                this.askRefresh()
            }
        }
    }

    static countdownFormatter = (props) => {

        if (props.hours > 6) {
            return "Sorry! This exhibition is closed";
        } else if (props.total <= 0) {
            return "Finishing up…";
        }

        let str = undefined;

        if (props.hours) {
            str = <span>Please come back in <b>${props.hours}:${props.formatted.minutes}:${props.formatted.seconds}</b>...</span>
        } else {
            str = <span>Please come back in <b>{props.minutes}:{props.formatted.seconds}</b>...</span>;
            // let roundedMinutes = props.minutes + 1;
            // let pS = roundedMinutes == 1 ? '' : 's';
            // str += `about ${roundedMinutes} minute${pS}`;
        }

        return str;
    }

    userInteraction = () => {
        if (this.openedTimeout) {
            this.clearOpenTimeout();
            this.registerOpenTimeout();
        }
    }


    render = () => {

        let modalEl = (<Modal
            show={this.state.modalOpen}
            onHide={this.closeModal}
            dialogClassName={"caide-modal" + (this.modalButtons.includes('CONSENT-NO-INSTA') ? " xl" : "")}
            backdrop={ this.modalStatic ? 'static' : true }
            centered
            keyboard={false}
        >
            <Modal.Header closeButton={this.closeButton}>
                <Modal.Title>{this.modalTitle}</Modal.Title>
            </Modal.Header>
            <Modal.Body>{this.modalBody}</Modal.Body>
            <Modal.Footer>
                { this.modalButtons.includes('PROGRESS-15') ?
                    (<div className="progressbar">
                        <svg className="progressbar__svg">
                            <circle cx="15" cy="15" r="14" className="progressbar__svg-circle circle-html anim-dur-15"></circle>
                        </svg>
                    </div>) : ''}

                { this.modalButtons.includes('PROGRESS-45') ?
                    (<div className="progressbar">
                        <svg className="progressbar__svg">
                            <circle cx="15" cy="15" r="14" className="progressbar__svg-circle circle-html anim-dur-45"></circle>
                        </svg>
                    </div>) : ''}

                { this.modalButtons.includes('PROGRESS-120') ?
                    (<div className="progressbar">
                        <svg className="progressbar__svg">
                            <circle cx="15" cy="15" r="14" className="progressbar__svg-circle circle-html anim-dur-120"></circle>
                        </svg>
                    </div>) : ''}

                { this.modalButtons.includes('EXPANDO') ? (<div className="expando"/>) : ''}

                { this.modalButtons.includes('OK-SAD') ? (<Button className="btn-scrapeelegy" variant="light" onClick={this.closeModal}>No thanks</Button>) : ''}
                { this.modalButtons.includes('DEMO') ? (<Button className="btn-scrapeelegy" onClick={this.noInstagramConfirm}>Hear our Scrape Elegy</Button>) : ''}

                { this.modalButtons.includes('OK') ? (<Button className="btn-scrapeelegy" onClick={this.closeModal}>Ok</Button>) : ''}
                { this.modalButtons.includes('CANCEL') ? (<Button className="btn-scrapeelegy" onClick={this.closeModal}>Cancel</Button>) : ''}
                { this.modalButtons.includes('CANCEL-FOLLOW') ? (<Button variant="light" className="btn-scrapeelegy" onClick={this.cancelFollow}>Cancel</Button>) : ''}
                { this.modalButtons.includes('DONE-FOLLOW') ? (<Button className="btn-scrapeelegy" onClick={this.doneFollow}>Done</Button>) : ''}

                { this.modalButtons.includes('SECRET-NO') ?  (<Button className="btn-scrapeelegy" variant="light" onClick={this.closeModal}>Cancel</Button>) : ''}
                { this.modalButtons.includes('SECRET-YES') ? (<Button className="btn-scrapeelegy" onClick={this.interruptSession}>Reset</Button>) : ''}

                { this.modalButtons.includes('REFRESH-NO') ?  (<Button className="btn-scrapeelegy" variant="light" onClick={this.closeModal}>Cancel</Button>) : ''}
                { this.modalButtons.includes('REFRESH-YES') ? (<Button className="btn-scrapeelegy" onClick={this.refresh}>Refresh</Button>) : ''}

                { this.modalButtons.includes('CONSENT-NO-INSTA') ? (<Button className="btn-scrapeelegy" variant="light"      onClick={this.consentNoInstagram}>I don't have Instagram</Button>) : ''}
                { this.modalButtons.includes('CONSENT-CONTINUE') ? (<Button className="btn-scrapeelegy"                      onClick={this.consentContinue}>Yes</Button>) : ''}

            </Modal.Footer>
        </Modal>)

        let component = '';

        if (this.state.state === 'unarmed') {

            component = (
<div onClick={this.tap} className={`Home ${this.state.openedClass} ${this.state.state} ${this.props.mode === 'AUXILIARY' ? 'auxiliary' : 'circle'}`}>
    <div className='lds-ellipsis clr'><div></div><div></div><div></div><div></div></div>

    { modalEl }
</div>)

        } else {

            component = (

<div onClick={this.tap} onKeyDownCapture={this.userInteraction} onMouseDownCapture={this.userInteraction}
     className={`Home ${this.state.openedClass} ${this.state.state} ${this.state.enterPrompt ? 'enter-prompt' : ''}  ${this.state.loadingState ? 'init_scrape_wait_resp' : ''} ${this.state.modalOpen ? 'modal-open' : ''} ${this.props.mode === 'AUXILIARY' ? 'auxiliary' : 'circle'}`}>
    <div className="temp-overlay"></div>
    <div className="splash-holder">
        <div className="splash splash-outer splash-1-outer">
            <div className="splash splash-inner splash-1"></div>
        </div>
        <div className="splash splash-outer splash-2-outer">
            <div className="splash splash-inner splash-2"></div>
        </div>
        <div className="splash splash-outer splash-3-outer">
            <div className="splash splash-inner splash-3"></div>
        </div>
    </div>

    <div className="title-holder">
        <div className="title">
            <div className="svgs">
                <div className="svgs-2">
                    <div className="svg-holder svg-holder-1">
                        <div className="svg-outer">
                            <svg width="100%" viewBox="0 0 40 40" className="svg-1">
                                <g className="marks">
                                    {[...Array(95)].map((elem, i) => <line key={i} x1={i % 2 == 0 ? 14 : 13.55} y1="0"
                                                                            x2={i % 2 == 0 ? 14.5 : 14.75}
                                                                            y2="0"/>)}
                                </g>
                            </svg>
                        </div>
                    </div>
                    <div className="svg-holder svg-holder-2">
                        <div className="svg-outer">
                            <svg width="100%" viewBox="0 0 40 40" className="svg-2">
                                <g className="marks">
                                    {[...Array(40)].map((elem, i) => <line key={i} x1="15.5" y1="0" x2="16.5" y2="0"/>)}
                                </g>
                            </svg>
                        </div>
                    </div>
                    <div className="svg-holder svg-holder-3">
                        <div className="svg-outer">
                            <svg width="100%" viewBox="0 0 40 40" className="svg-3">
                                <g className="marks">
                                    {[...Array(15)].map((elem, i) => <line key={i} x1="16.5" y1="0" x2="20" y2="0"/>)}
                                </g>
                            </svg>
                        </div>
                    </div>
                    <div className="svg-holder svg-holder-4">
                        <div className="svg-outer">
                            <svg width="100%" viewBox="0 0 40 40" className="svg-4">
                                <circle cx="20" cy="20" r="17"/>
                                <circle cx="20" cy="20" r="15"/>
                                <circle cx="20" cy="20" r="10"/>
                                <g className="marks">
                                    {[...Array(50)].map((elem, i) => <line key={i} x1="7.3" y1="0" x2="8.1" y2="0"/>)}
                                </g>
                            </svg>
                        </div>
                    </div>
                </div>
            </div>
            <div className="title-2">
                <div className="title-3">
                    <div>VACANT</div>
                </div>

                <div className="subtitle-2">
                    <div className="subtitle-3">
                        Please Enter
                    </div>
                </div>
            </div>
        </div>
    </div>



    <div className="button-holder">
        <Button variant="outline-light" className="caide-button start-button" onClick={this.startClicked} >
            <div className="button-splash"></div>
            <div className="button-text">Start <FontAwesomeIcon icon={faChevronRight} size="xs" /></div>
        </Button>
    </div>

    <Start ref={this.formRef} genericError={this.genericError} close={this.close} startedLoading={this.startedLoading} getParentState={this.getLifecycleState} isLoading={this.state.loadingState}></Start>



    {modalEl}

    <div className="occupied-holder" >
        <div className="occupied-banner">OCCUPIED</div>
        <div className="occupied-notice">
            <Countdown
                date={this.state.eta}
                renderer={Home.countdownFormatter}
                key={this.state.eta} // Whenever eta changes, the key changes, and the countdown restarts. Dumb component.
            />
        </div>
    </div>

    <div className="border-holder"></div>

    <div className="loading">

        <div className="loader">
            <div className="lds-ellipsis"><div></div><div></div><div></div><div></div></div>
        </div>

    </div>

    <div className="eye-fade"></div>

</div>
);

        }

        return component;
    }
}

export default Home;