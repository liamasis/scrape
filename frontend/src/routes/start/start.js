import Form from "react-bootstrap/Form";
import Button from "react-bootstrap/Button";
import React from "react";
import Container from 'react-bootstrap/Container'
import Row from 'react-bootstrap/Row'
import Col from 'react-bootstrap/Col'

import "./start.scss"
import FormControl from "react-bootstrap/FormControl";
import InputGroup from "react-bootstrap/InputGroup";
import App from "../../App";
import {default as axios} from "axios";

import Keyboard from "react-simple-keyboard";
import "react-simple-keyboard/build/css/index.css";
import {faDeleteLeft, faChevronLeft} from "@fortawesome/free-solid-svg-icons";
import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";

import { renderToStaticMarkup } from 'react-dom/server';

import { isTablet } from 'react-device-detect';

import {rgbLogShade, m32, cubicBezier, clamp, custom} from "../../utils";

const WORD_FLASH = ['CRINGE', 'IS A', 'TYPE', 'OF SMALL', 'DEATH', 'AN', 'ELEGY', 'IS A', 'MOURNING', 'POEM', 'SCRAPING',
    'IS', 'WHAT IS', 'DONE', 'TO OUR', 'DATA', 'BEHIND', 'THE SCENE', 'OF', 'EXTRACTIVE', 'CAPITALISM', 'WTF', 'YUCK MACHINE',
    'QUIET', 'PLACES', 'TO REFLECT', 'ARE A', 'ROMANTIC', 'NOTION', 'THAT', 'DON’T', 'LIKE', 'EXIST', '1M BORED', 'BY HAVING', 'TO CARE',
    'ABOUT', 'HOW', '1DK', 'IM BEING', 'YES', 'STOLEN', '0MG', 'TAKE ME', 'TO', 'LIKE', 'WTF?', 'THE D33P', 'HAH4', 'MAKE ME', 'QU4NTUM',
    'HIII11', 'LOVE Y0U', 'SLE3P', '0MG', 'SL3EP', '0MFG', 'TY', '1DK', 'SNH', 'TLDR', 'TLDR', 'TLDR', 'TLDR', 'TLDR', 'TLDR']


class Start extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            wordFlashPos: 0,
            instagramHandle: '',
            layoutName: 'default' // For keyboard
        };
    }


    onChange = input => {
        this.setState({instagramHandle: input});
        console.log("Input changed", input);
    };

    onKeyPress = button => {
        console.log("Button pressed", button);

        /**
         * If you want to handle the shift and caps lock buttons
         */
        if (button === "{shift}" || button === "{lock}") this.handleShift();
    };

    handleShift = () => {
        const layoutName = this.state.layoutName;

        this.setState({
            layoutName: layoutName === "default" ? "shift" : "default"
        });
    };






    clearHandle = () => {
        this.setState({
            instagramHandle: '',
            wordFlashPos: 0
        });
        this.keyboard.clearInput();
    }


    handleInputChange = (event) => {
        const target = event.target;
        const value = target.type === 'checkbox' ? target.checked : target.value;
        const name = target.name;

        this.setState({
            [name]: value
        });

        // Keyboard thing
        this.keyboard.setInput(value);
    }

    handleSubmit = (event) => {
        event.preventDefault();

        if(this.props.getParentState() !== 'ready') {
            return;
        }

        this.props.startedLoading()
        this.startWordFlash()

        axios.post("/api/scrape", {instagramHandle: this.state.instagramHandle}, {withCredentials: false})
            .then((result) => {
                console.log("Hooray!")
            })
            .catch((error) => {
                this.props.genericError();
            });

    }


    // _csrfToken = null;
    //
    // getCsrfToken = async () => {
    //   if (this._csrfToken === null) {
    // 	const response = await fetch(`/csrf/`, {
    // 	  credentials: 'include',
    // 	});
    // 	const data = await response.json();
    // 	this._csrfToken = data.csrfToken;
    //   }
    //   return this._csrfToken;
    // }

    close = () => {
        document.activeElement.blur();
        this.setState({
            instagramHandle: ''
        })
        this.props.close()
    }


    startWordFlash = () => {
        this.clearWordFlash()
        this.seed = Math.floor(Math.random() * 100000)
        this.setState({wordFlashOn: true, wordFlashPos: 0})
        setTimeout(this.wordFlashStep, 300)
    }

    clearWordFlash = () => {
        if (this.wordFlashTimeout) clearTimeout(this.wordFlashTimeout)
    }

    wordFlashStep = () => {
        if(!this.props.isLoading) return;

        this.setState((state, props) => ({ wordFlashPos: state.wordFlashPos + 1 }) )

        const time = this.time(this.state.wordFlashPos);
        console.log(`${this.state.wordFlashPos}: ${time}`);

        if (this.state.wordFlashPos <= WORD_FLASH.length - 1) {
            this.wordFlashTimeout = setTimeout(this.wordFlashStep, time)
        } else if (this.state.wordFlashPos == WORD_FLASH.length) {
            this.wordFlashTimeout = setTimeout(this.startWordFlash, 2000)
        }
    }

    time = (idx) => {
        // const LIN_CAP = 37;
        // if (idx >= LIN_CAP) {
        //     return 205 - clamp((idx - LIN_CAP) / (WORD_FLASH.length - LIN_CAP), 0, 1) * 130
        // }
        // const prog = custom(clamp(idx / WORD_FLASH.length, 0, 1), 1, 1)
        // const time = 600 - (410 * prog)


        const prog = cubicBezier(clamp(idx / WORD_FLASH.length, 0, 1), 1, 0.57)
        const time = 550 - (480 * prog)

        // const time = 600 - clamp(idx / 40, 0, 1) * 450
        return time;
    }


    render() {

        // animation: ;
        const wordFlashContents = !this.props.isLoading ? '' : WORD_FLASH.slice(0, this.state.wordFlashPos).map((text, index) =>
            {

                let idx = Math.floor(m32(this.seed + index) * 6)
                // let idx = 3
                let lighten = m32(2 * this.seed + index)
                let time = this.time(idx)
                let fontSize = 3.5 + 2.5 * m32(3 * this.seed + index)

                if (index === WORD_FLASH.length - 3) {
                    idx = 2;
                    time = 1200;
                    fontSize = 5.5
                    lighten = 0.1
                }

                if (index === WORD_FLASH.length - 2) {
                    idx = 2;
                    time = 1200;
                    fontSize = 5
                    lighten = 0.4
                }

                if (index === WORD_FLASH.length - 1) {
                    idx = 2;
                    time = 1200;
                    fontSize = 4.5
                    lighten = 0.7
                }

                let style = {
                    animation: `flash-fade-${idx} ${time}ms forwards`,
                    color: rgbLogShade(lighten, 'rgb(251, 199, 181)'),
                    fontSize: `${fontSize}rem`
                };



                // if (index === WORD_FLASH.length - 1) {
                //     style = {
                //         color: 'white',
                //         fontSize: `5.25rem`
                //     };
                // }

                return (
                    <div className="word-flash-inner" key={index} >
                        <div className="word-flash" style={style}>{text}</div>
                    </div>
                )
            }
        )

        return (
            <div className={`slide-out`}>

                <div className="slide-back-holder">
                    <Button type="submit" size="lg" variant="outline-light" className="icon-button" onClick={this.close}>
                        <FontAwesomeIcon icon={faChevronLeft} />
                    </Button>
                </div>

                <Form onSubmit={this.handleSubmit}>

                    <div className="body">

                        <div className="slide-container">

                            <InputGroup size="lg" className="xl" >
                                <InputGroup.Text>
                                    <div>@</div>
                                </InputGroup.Text>
                                <FormControl required aria-required name="instagramHandle"
                                             value={this.state.instagramHandle}
                                             onChange={this.handleInputChange}
                                             placeholder="Instagram Handle"
                                             aria-label="Instagram Handle"
                                             readOnly={isTablet}
                                />
                            </InputGroup>

                            <Button type="submit" size="lg" className="btn-scrapeelegy xl">
                                <div className="button-text">Go</div>
                            </Button>


                        </div>
                    </div>

                </Form>

                <div className="keyboard">

                    <Keyboard
                        keyboardRef={r => (this.keyboard = r)}
                        layoutName={this.state.layoutName}
                        onChange={this.onChange}
                        onKeyPress={this.onKeyPress}

                        display={{
                            '{bksp}': renderToStaticMarkup(<FontAwesomeIcon icon={faDeleteLeft} />),
                        }}

                        layout={{
                            default: [
                                "1 2 3 4 5 6 7 8 9 0 _ {bksp}",     // 12
                                "q w e r t y u i o p",              // 10
                                "a s d f g h j k l",                // 9
                                "z x c v b n m .",                  // 8
                                // "{shift} {space}"
                            ],
                            // shift: [
                            //     "! @ # $ % ^ & * ( ) _ {bksp}",
                            //     "Q W E R T Y U I O P",
                            //     'A S D F G H J K L',
                            //     "Z X C V B N M ?",
                            //     // "{shift} {space}"
                            // ]
                        }}

                    />

                </div>


                <div className="word-flash-outer">
                    {wordFlashContents}
                </div>



            </div>
        );
    }
}

export default Start;