<p align="center"><img src="https://www.janestreet.com/assets/email-templates/etc-logo.png" alt="Jane Steet ETC Logo" /></p>

<h1 align="center">Jane Street - NUS Virtual Electronic Trading Challenge (ETC)</h1>

Jane Street ETC is a day-long programming contest where participants compete against each other in a simulated market. Participating teams wrote algorithms to trade various financial instruments such as bonds, stocks, ETFs, and ADRs, with the intention of maximizing profit.

The challenge comprised of two competitions which were both structured into five minute rounds, with two teams pitted against each other every round. During the first competition, teams traded and built up their algorithms for seven hours. In the last hour, a simultaneous competition, "The Final Hour", was held, allowing teams to compete in a second competition with the best version of their bots.

In both competitions, our team placed **2nd** out of 15 teams. Unfortunately, that meant no prizes for us, since only the first places were awarded.

## Team: College Ave East

- Ho Jie Feng ([@hojiefeng](https://github.com/hojiefeng))
- James Tan ([@iamjamestan](https://github.com/iamjamestan))
- Sun Yitao ([@sun-yitao](https://github.com/sun-yitao))
- Zhu Hanming ([@zhuhanming](https://github.com/zhuhanming))

## Strategies

Below are some of the strategies that we have employed in our algorithm:

### BOND Strategy

We used a very simple strategy for bonds, with a slight speed optimization. Put simply, we sell when the price is above 1000 and buy when price is below 1000. And we do that for all bonds that meet this criteria at any point in time, allowing us to reap quick and steady benefits.

### ADR Strategy

For our ADR strategy, we compared the value of the common stock VALBZ to its illiquid ADR counterpart, VALE, by taking the average of their 10 most recent trade prices. If the value of VALE was lower than that of VALBZ by at least 2 dollars, we will place orders to buy VALE, convert VALE to VALBZ, and then sell VALBZ.

### XLF Strategy

We computed the value of basket of stocks under the ETF which would be more liquid than the ETF itself and closer to the fair market value. If the difference between the basket value and the ETF exceeds the conversion cost plus a small buffer, we will convert from the ETF constituents to the ETF, and vice versa.
