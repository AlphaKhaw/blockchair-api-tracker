<div id="top"></div>
<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/AlphaKhaw/blockchair-api-tracker">
    <img src="https://user-images.githubusercontent.com/87654386/186582833-219762e2-0198-4bb4-ade7-b1028e66d360.png" alt="Logo" width="200" height="150">
  </a>

<h3 align="center">Blockchair API Tracker</h3>

  <p align="center">
    A github repository utilising Blockchair API to build a cryptocurrency address tracker
    <br />
    <a href="https://github.com/AlphaKhaw/blockchair-api-tracker"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/AlphaKhaw/blockchair-api-tracker">View Demo</a>
    ·
    <a href="https://github.com/AlphaKhaw/blockchair-api-tracker/issues">Report Bug</a>
    ·
    <a href="https://github.com/AlphaKhaw/blockchair-api-tracker/issues">Request Feature</a>
  </p>
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>


<!-- ABOUT THE PROJECT -->
## About The Project

This project aims to utilise various blockchain entities endpoints available on Blockchair API to build a tracker for blockchain address(es). Currently, 
`blockchair.py` caters to Bitcoin and Ethereum addresses input with the two most popular blockchain in mind. User can utilise this repository to customise and keep track of their personal cryptocurrency portfolios. Another potential use case is for user to scrape transaction history of target address(es). 

Blockchair API currently supports/provides endpoints for the following blockchains: 
* Bitcoin
* Ethereum 
* Litecoin 
* Cardano
* Ripple
* Polkadot
* Dogecoin
* Bitcoin Cash
* Solana
* Stellar
* Monero
* EOS
* Kusama
* Bitcoin SV
* eCash
* Zcash
* Dash
* Mixin
* Groestlcoin

Note: Kindly refer to [Blockchair Website](https://blockchair.com/about#:~:text=Blockchair%20is%20a%20blockchain%20search,of%20blockchain%20explorers%20on%20steroids/)
for more updated information on support blockchains. 

### Built with

* [Blockchair API](https://blockchair.com/api/docs)

<p align="right">(<a href="#top">back to top</a>)</p>


<!-- GETTING STARTED -->
## Getting Started

### Prerequisites

[Blockchair API Pricing Plan](https://blockchair.com/api/plans)

**Note**: One can utilise the repository and Blockchair API without an API key. However, there will be an imposed limitation on the number of API calls allowed. 

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- USAGE EXAMPLES -->
## Usage

| `blockchair.py` - 
- Code with required input arguments to initialise Blockchair class: 
 ```py
if __name__ == '__main__':
    blockchair = Blockchair(address=BLOCKCHAIN_ADDRESS, 
                            file_name=SAVED_FILE_NAME, 
                            api_key=OPTIONAL)       
   ```

_For more examples, please refer to the [Documentation](https://github.com/AlphaKhaw/blockchair-api-tracker)

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- ROADMAP -->
## Roadmap

- [ ] Expanding beyond Bitcoin and Ethereum classes to cater for alternative endpoints 
- [ ] Experimenting with `Raw data endpoints` and `Infinitable endpoints` provided by Blockchair API to potentially optimise current solution

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- CONTACT -->
## Contact

Khaw Jiahao - [Linkedin](https://www.linkedin.com/in/khaw-jia-hao-65832217b/) - alphakhaw@gmail.com

Project Link: [https://github.com/AlphaKhaw/blockchair-api-tracker](https://github.com/AlphaKhaw/blockchair-api-tracker")

<p align="right">(<a href="#top">back to top</a>)</p>
