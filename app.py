"""Monthly bilateral real exchange rates from the IMF. Python 3.12."""

from datetime import date, datetime, timezone
from io import StringIO
import re
import xml.etree.ElementTree as ET

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import streamlit as st


BASE = "https://api.imf.org/external/sdmx/3.0"
FIRST_MONTH = "1976-01"
# IMF CL_COUNTRY snapshot, downloaded 2026-10-26. Used only if metadata is offline.
COUNTRY_SNAPSHOT = {'ABW': 'Aruba, Kingdom of the Netherlands',
 'AFG': 'Afghanistan, Islamic Republic of',
 'AFR': 'Africa (AFR)',
 'AGO': 'Angola',
 'AIA': 'Anguilla, United Kingdom-British Overseas Territory',
 'ALA': 'Åland Islands',
 'ALB': 'Albania',
 'AND': 'Andorra, Principality of',
 'ANT': 'Netherlands Antilles',
 'APD': 'Asia and Pacific (APD)',
 'ARE': 'United Arab Emirates',
 'ARG': 'Argentina',
 'ARM': 'Armenia, Republic of',
 'ASM': 'American Samoa',
 'ATF': 'French Southern Territories',
 'ATG': 'Antigua and Barbuda',
 'AUS': 'Australia',
 'AUT': 'Austria',
 'AZE': 'Azerbaijan, Republic of',
 'BDI': 'Burundi',
 'BEL': 'Belgium',
 'BEN': 'Benin',
 'BES': 'Bonaire, Saint Eustatius and Saba',
 'BFA': 'Burkina Faso',
 'BGD': 'Bangladesh',
 'BGR': 'Bulgaria',
 'BHR': 'Bahrain, Kingdom of',
 'BHS': 'Bahamas, The',
 'BIH': 'Bosnia and Herzegovina',
 'BLM': 'Saint Barthelemy',
 'BLR': 'Belarus, Republic of',
 'BLZ': 'Belize',
 'BMU': 'Bermuda',
 'BOL': 'Bolivia',
 'BRA': 'Brazil',
 'BRB': 'Barbados',
 'BRN': 'Brunei Darussalam',
 'BTN': 'Bhutan',
 'BVT': 'Bouvet Island',
 'BWA': 'Botswana',
 'CAF': 'Central African Republic',
 'CAN': 'Canada',
 'CCK': 'Cocos Islands',
 'CHE': 'Switzerland',
 'CHL': 'Chile',
 'CHN': "China, People's Republic of",
 'CIV': "Côte d'Ivoire",
 'CMR': 'Cameroon',
 'COD': 'Congo, Democratic Republic of the',
 'COG': 'Congo, Republic of',
 'COK': 'Cook Islands',
 'COL': 'Colombia',
 'COM': 'Comoros, Union of the',
 'CPV': 'Cabo Verde',
 'CRI': 'Costa Rica',
 'CSK': 'Czechoslovakia',
 'CUB': 'Cuba',
 'CUW': 'Curaçao, Kingdom of the Netherlands',
 'CWX': 'Curaçao and Sint Maarten',
 'CXR': 'Christmas Island',
 'CYM': 'Cayman Islands',
 'CYP': 'Cyprus',
 'CZE': 'Czech Republic',
 'DDR': 'German Democratic Republic',
 'DEU': 'Germany',
 'DJI': 'Djibouti',
 'DMA': 'Dominica',
 'DNK': 'Denmark',
 'DOM': 'Dominican Republic',
 'DZA': 'Algeria',
 'ECU': 'Ecuador',
 'EGY': 'Egypt, Arab Republic of',
 'ERI': 'Eritrea, The State of',
 'ESH': 'Western Sahara',
 'ESP': 'Spain',
 'EST': 'Estonia, Republic of',
 'ETH': 'Ethiopia, The Federal Democratic Republic of',
 'EUR': 'Europe (EUR)',
 'FIN': 'Finland',
 'FJI': 'Fiji, Republic of',
 'FLK': 'Falkland Islands (Malvinas)',
 'FRA': 'France',
 'FRO': 'Faroe Islands',
 'FSM': 'Micronesia, Federated States of',
 'G163': 'Euro Area (EA)',
 'GAB': 'Gabon',
 'GBR': 'United Kingdom',
 'GEO': 'Georgia',
 'GGY': 'Guernsey',
 'GHA': 'Ghana',
 'GIB': 'Gibraltar',
 'GIN': 'Guinea',
 'GLP': 'Guadeloupe',
 'GMB': 'Gambia, The',
 'GNB': 'Guinea-Bissau',
 'GNQ': 'Equatorial Guinea, Republic of',
 'GRC': 'Greece',
 'GRD': 'Grenada',
 'GRL': 'Greenland',
 'GTM': 'Guatemala',
 'GUF': 'French Guiana',
 'GUM': 'Guam',
 'GUY': 'Guyana',
 'HKG': "Hong Kong Special Administrative Region, People's Republic of China",
 'HMD': 'Heard Island and McDonald Islands',
 'HND': 'Honduras',
 'HRV': 'Croatia, Republic of',
 'HTI': 'Haiti',
 'HUN': 'Hungary',
 'IDN': 'Indonesia',
 'IMN': 'Isle of Man',
 'IND': 'India',
 'IOT': 'British Indian Ocean Territory',
 'IRL': 'Ireland',
 'IRN': 'Iran, Islamic Republic of',
 'IRQ': 'Iraq',
 'ISL': 'Iceland',
 'ISR': 'Israel',
 'ITA': 'Italy',
 'JAM': 'Jamaica',
 'JEY': 'Jersey',
 'JOR': 'Jordan',
 'JPN': 'Japan',
 'KAZ': 'Kazakhstan, Republic of',
 'KEN': 'Kenya',
 'KGZ': 'Kyrgyz Republic',
 'KHM': 'Cambodia',
 'KIR': 'Kiribati',
 'KNA': 'St. Kitts and Nevis',
 'KOR': 'Korea, Republic of',
 'KOS': 'Kosovo, Republic of',
 'KWT': 'Kuwait',
 'LAO': "Lao People's Democratic Republic",
 'LBN': 'Lebanon',
 'LBR': 'Liberia',
 'LBY': 'Libya',
 'LCA': 'St. Lucia',
 'LIE': 'Liechtenstein, Principality of',
 'LKA': 'Sri Lanka',
 'LSO': 'Lesotho, Kingdom of',
 'LTU': 'Lithuania, Republic of',
 'LUX': 'Luxembourg',
 'LVA': 'Latvia, Republic of',
 'MAC': "Macao Special Administrative Region, People's Republic of China",
 'MAF': 'Saint Martin',
 'MAR': 'Morocco',
 'MCD': 'Middle East and Central Asia (MCD)',
 'MCO': 'Monaco',
 'MDA': 'Moldova, Republic of',
 'MDG': 'Madagascar, Republic of',
 'MDV': 'Maldives',
 'MEX': 'Mexico',
 'MHL': 'Marshall Islands, Republic of the',
 'MKD': 'North Macedonia, Republic of',
 'MLI': 'Mali',
 'MLT': 'Malta',
 'MMR': 'Myanmar',
 'MNE': 'Montenegro',
 'MNG': 'Mongolia',
 'MNP': 'Northern Mariana Islands',
 'MOZ': 'Mozambique, Republic of',
 'MRT': 'Mauritania, Islamic Republic of',
 'MSR': 'Montserrat, United Kingdom-British Overseas Territory',
 'MTQ': 'Martinique',
 'MUS': 'Mauritius',
 'MWI': 'Malawi',
 'MYS': 'Malaysia',
 'MYT': 'Mayotte',
 'NAM': 'Namibia',
 'NCL': 'New Caledonia',
 'NER': 'Niger',
 'NFK': 'Norfolk Island',
 'NGA': 'Nigeria',
 'NIC': 'Nicaragua',
 'NIU': 'Niue',
 'NLD': 'Netherlands, The',
 'NOR': 'Norway',
 'NPL': 'Nepal',
 'NRU': 'Naoero, Republic of',
 'NZL': 'New Zealand',
 'OMN': 'Oman',
 'PAK': 'Pakistan',
 'PAN': 'Panama',
 'PCN': 'Pitcairn Islands',
 'PER': 'Peru',
 'PHL': 'Philippines',
 'PLW': 'Palau, Republic of',
 'PNG': 'Papua New Guinea',
 'POL': 'Poland, Republic of',
 'PRI': 'Puerto Rico',
 'PRK': "Korea, Democratic People's Republic of",
 'PRT': 'Portugal',
 'PRY': 'Paraguay',
 'PYF': 'French Polynesia',
 'QAT': 'Qatar',
 'REU': 'Réunion',
 'ROU': 'Romania',
 'RUS': 'Russian Federation',
 'RWA': 'Rwanda',
 'SAU': 'Saudi Arabia',
 'SCG': 'Serbia and Montenegro',
 'SDN': 'Sudan',
 'SDS': 'Small Developing States (SDS)',
 'SEN': 'Senegal',
 'SGP': 'Singapore',
 'SGS': 'South Georgia and the South Sandwich Islands',
 'SHN': 'St. Helena',
 'SJM': 'Svalbard and Jan Mayen Islands',
 'SLB': 'Solomon Islands',
 'SLE': 'Sierra Leone',
 'SLV': 'El Salvador',
 'SMR': 'San Marino, Republic of',
 'SOM': 'Somalia',
 'SPM': 'St. Pierre and Miquelon',
 'SRB': 'Serbia, Republic of',
 'SSD': 'South Sudan, Republic of',
 'STP': 'São Tomé and Príncipe, Democratic Republic of',
 'SUN': 'Union of Soviet Socialist Republics (USSR)',
 'SUR': 'Suriname',
 'SVK': 'Slovak Republic',
 'SVN': 'Slovenia, Republic of',
 'SWE': 'Sweden',
 'SWZ': 'Eswatini, Kingdom of',
 'SXM': 'Sint Maarten, Kingdom of the Netherlands',
 'SYC': 'Seychelles',
 'SYR': 'Syrian Arab Republic',
 'TCA': 'Turks and Caicos Islands',
 'TCD': 'Chad',
 'TGO': 'Togo',
 'THA': 'Thailand',
 'TJK': 'Tajikistan, Republic of',
 'TKL': 'Tokelau',
 'TKM': 'Turkmenistan',
 'TLS': 'Timor-Leste, Democratic Republic of',
 'TON': 'Tonga',
 'TTO': 'Trinidad and Tobago',
 'TUN': 'Tunisia',
 'TUR': 'Türkiye, Republic of',
 'TUV': 'Tuvalu',
 'TWN': 'Taiwan Province of China',
 'TZA': 'Tanzania, United Republic of',
 'UGA': 'Uganda',
 'UKR': 'Ukraine',
 'UMI': 'United States Minor Outlying Islands',
 'URY': 'Uruguay',
 'USA': 'United States',
 'UZB': 'Uzbekistan, Republic of',
 'VAT': 'Holy See',
 'VCT': 'St. Vincent and the Grenadines',
 'VDR': 'Vietnam, Democratic Republic of',
 'VEN': 'Venezuela, República Bolivariana de',
 'VGB': 'British Virgin Islands',
 'VIR': 'United States Virgin Islands',
 'VNM': 'Vietnam',
 'VUT': 'Vanuatu',
 'WBG': 'West Bank and Gaza',
 'WHD': 'Western Hemisphere (WHD)',
 'WLF': 'Wallis and Futuna Islands',
 'WSM': 'Samoa',
 'YAR': 'Yemen Arab Republic',
 'YEM': 'Yemen, Republic of',
 'YMD': "Yemen, People's Democratic Republic of",
 'YUG': 'Yugoslavia, Socialist Federal Republic of',
 'ZAF': 'South Africa',
 'ZMB': 'Zambia',
 'ZWE': 'Zimbabwe'}


class IMFError(RuntimeError):
    """An actionable data-source error that can be displayed to the user."""


def request_imf(url, accept, params=None):
    """Bounded retries, explicit format negotiation, and URL-rich errors."""
    retry = Retry(total=2, backoff_factor=0.7, status_forcelist=[429, 500, 502, 503, 504],
                  allowed_methods=["GET"], respect_retry_after_header=False)
    with requests.Session() as session:
        session.mount("https://", HTTPAdapter(max_retries=retry))
        try:
            response = session.get(url, params=params, headers={"Accept": accept},
                                   timeout=(10, 35))
            response.raise_for_status()
        except requests.RequestException as exc:
            raise IMFError(f"IMF download failed: {exc}\nRequested endpoint: {url}") from exc
    return response


def parse_countries(xml_text):
    root = ET.fromstring(xml_text)
    countries = {}
    for codelist in root.iter():
        if codelist.tag.rsplit("}", 1)[-1] != "Codelist" or codelist.get("id") != "CL_COUNTRY":
            continue
        for code in codelist:
            identifier = code.get("id", "")
            if not re.fullmatch(r"[A-Z]{3}|G163", identifier):
                continue
            for name in code:
                if (name.tag.rsplit("}", 1)[-1] == "Name"
                        and name.get("{http://www.w3.org/XML/1998/namespace}lang") == "en"):
                    countries[identifier] = name.text or identifier
    if not {"GBR", "USA", "G163"}.issubset(countries):
        raise IMFError("The IMF country list is missing required entries.")
    return countries


@st.cache_data(ttl=604800, show_spinner=False)
def load_countries():
    try:
        response = request_imf(f"{BASE}/structure/codelist/IMF/CL_COUNTRY/~",
                               "application/vnd.sdmx.structure+xml;version=3.0.0")
        return parse_countries(response.text), "Live IMF country list"
    except (IMFError, ET.ParseError) as exc:
        return COUNTRY_SNAPSHOT.copy(), f"Saved IMF country list (2026-10-26). {exc}"


def parse_observations(text, country, kind, price_type="CPI"):
    """Validate a single monthly series and preserve the IMF input attributes."""
    empty = pd.DataFrame(index=pd.DatetimeIndex([], name="month"), columns=["value"])
    if not text.strip():
        return empty
    try:
        raw = pd.read_csv(StringIO(text), dtype=str, keep_default_na=False)
    except (pd.errors.ParserError, pd.errors.EmptyDataError) as exc:
        raise IMFError("The IMF response could not be read as CSV.") from exc
    raw.columns = raw.columns.str.strip().str.lstrip("\ufeff")
    expected = {"COUNTRY": country, "FREQUENCY": "M",
                "TYPE_OF_TRANSFORMATION": "IX" if kind == "CPI" else "PA_RT"}
    if kind == "CPI":
        expected.update({"INDEX_TYPE": price_type, "COICOP_1999": "_T"})
    else:
        expected["INDICATOR"] = "XDC_USD"
    required = {"TIME_PERIOD", "OBS_VALUE", *expected}
    if not required.issubset(raw.columns):
        raise IMFError("IMF returned an unexpected format; expected monthly SDMX CSV. "
                       f"Columns received: {list(raw.columns)}")
    for column, value in expected.items():
        raw = raw.loc[raw[column].eq(value)].copy()
    if raw.empty:
        return empty
    periods = raw["TIME_PERIOD"].str.replace("-M", "-", regex=False)
    if not periods.str.fullmatch(r"\d{4}-\d{2}").all():
        raise IMFError("Unexpected monthly time labels in the IMF response.")
    raw.index = pd.DatetimeIndex(pd.to_datetime(periods, format="%Y-%m"), name="month")
    if raw.index.has_duplicates:
        raise IMFError("IMF returned multiple observations for one month. "
                       "The app will not silently average or discard them.")
    values = pd.to_numeric(raw["OBS_VALUE"], errors="coerce")
    # IMF SCALE is a power of ten; keep both original and scaled values in the CSV.
    scale_text = raw["SCALE"] if "SCALE" in raw else pd.Series("0", index=raw.index)
    scales = pd.to_numeric(scale_text.replace("", "0"), errors="coerce")
    if scales.isna().any():
        raise IMFError("An IMF scale factor is not numeric.")
    raw.insert(0, "value", values * np.power(10.0, scales))
    return raw.loc[raw.index >= FIRST_MONTH].sort_index()


@st.cache_data(ttl=86400, show_spinner=False)
def load_series(country, kind):
    price_type = "CPI"
    while True:
        key = (f"{country}.{price_type}._T.IX.M" if kind == "CPI"
               else f"{country}.XDC_USD.PA_RT.M")
        url = f"{BASE}/data/dataflow/IMF.STA/{kind}/~/{key}"
        response = request_imf(url, "text/csv", {"c[TIME_PERIOD]": "ge:1976-M01"})
        data = parse_observations(response.text, country, kind, price_type)
        # The Euro area's consumer-price measure is HICP in this IMF dataset.
        # Never substitute another country's observations or invent historical data.
        if (kind == "CPI" and country == "G163" and price_type == "CPI"
                and pd.to_numeric(data["value"], errors="coerce").notna().sum() == 0):
            price_type = "HICP"
            continue
        return data, {"series_key": key, "source_url": response.url,
                      "retrieved_utc": datetime.now(timezone.utc).isoformat(),
                      "price_type": price_type if kind == "CPI" else ""}


def calculate_sample(inputs, start, end):
    """FX inputs are currency/USD. RER* uses only valid months in this sample."""
    first, last = pd.Timestamp(start), pd.Timestamp(end)
    if first > last:
        raise ValueError("Start month must be on or before end month.")
    sample = inputs.reindex(pd.date_range(first, last, freq="MS", name="month")).copy()
    for column in ["P1", "P2", "FX1_LCU_per_USD", "FX2_LCU_per_USD"]:
        sample[column] = pd.to_numeric(sample[column], errors="coerce")
    positive = lambda s: s.notna() & np.isfinite(s) & s.gt(0)
    fx_valid = positive(sample.FX1_LCU_per_USD) & positive(sample.FX2_LCU_per_USD)
    sample["S_C2_per_C1"] = (sample.FX2_LCU_per_USD / sample.FX1_LCU_per_USD).where(fx_valid)
    sample["S_C2_per_C1"] = sample.S_C2_per_C1.where(positive(sample.S_C2_per_C1))
    valid = positive(sample.S_C2_per_C1) & positive(sample.P1) & positive(sample.P2)
    sample["RER"] = (sample.S_C2_per_C1 * sample.P1 / sample.P2).where(valid)
    sample["RER"] = sample.RER.where(positive(sample.RER))
    sample["valid_RER"] = sample.RER.notna()
    benchmark = sample.loc[sample.valid_RER, "RER"].mean()
    sample["RER_star"] = benchmark
    sample["Real_Index"] = 100.0 * sample.RER / benchmark
    sample["sample_start"] = start
    sample["sample_end"] = end
    return sample


def build_chart(sample, mode, nominal_units):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    if mode in ("Real", "Both"):
        fig.add_trace(go.Scatter(x=sample.index, y=sample.Real_Index, name="Real index",
                                line={"color": "#146C94", "width": 2}, connectgaps=False,
                                hovertemplate="%{x|%Y-%m}<br>Real index: %{y:.4f}<extra></extra>"),
                      secondary_y=False)
        fig.add_hline(y=100, line_dash="dot", line_color="#8696A0", secondary_y=False)
    if mode in ("Nominal", "Both"):
        fig.add_trace(go.Scatter(x=sample.index, y=sample.S_C2_per_C1, name="Nominal S",
                                line={"color": "#C26929", "width": 2}, connectgaps=False,
                                hovertemplate="%{x|%Y-%m}<br>S: %{y:.6f}<extra></extra>"),
                      secondary_y=(mode == "Both"))
    fig.update_yaxes(title_text=nominal_units if mode == "Nominal" else "Real index (sample mean = 100)",
                     secondary_y=False)
    fig.update_yaxes(title_text=nominal_units if mode == "Both" else None,
                     visible=(mode == "Both"), showgrid=False, secondary_y=True)
    fig.update_layout(height=500, hovermode="x unified", template="plotly_white",
                      margin={"l": 20, "r": 20, "t": 30, "b": 20},
                      legend={"orientation": "h", "y": 1.12},
                      xaxis={"title": "Month", "rangeslider": {"visible": True}})
    return fig


def currency_label(code, countries):
    return {"GBR": "GBP", "USA": "USD", "G163": "EUR"}.get(code, f"{countries[code]} currency")


def main():
    st.set_page_config(page_title="Real Exchange Rate Explorer", page_icon="🌐", layout="wide")
    st.title("Real Exchange Rate Explorer")
    st.write("Compare monthly purchasing-power movements using IMF consumer prices and exchange rates.")
    countries, country_note = load_countries()
    if country_note != "Live IMF country list":
        st.warning("IMF country metadata is temporarily unavailable. Using a saved IMF country list.")
        with st.expander("Country-list download details"):
            st.text(country_note)
    codes = sorted(countries, key=lambda c: countries[c])
    months = pd.period_range(FIRST_MONTH, date.today().strftime("%Y-%m"), freq="M").astype(str).tolist()
    with st.sidebar:
        st.header("Choose your comparison")
        c1 = st.selectbox("Country 1", codes, index=codes.index("GBR"),
                          format_func=lambda c: f"{countries[c]} ({c})", key="country1")
        c2 = st.selectbox("Country 2", codes, index=codes.index("USA"),
                          format_func=lambda c: f"{countries[c]} ({c})", key="country2")
        start = st.selectbox("Start month", months, index=0, key="start_month")
        end = st.selectbox("End month", months, index=len(months) - 1, key="end_month")
        mode = st.radio("Chart", ["Real", "Nominal", "Both"], index=2, horizontal=True, key="mode")
        if st.button("Refresh IMF data"):
            load_countries.clear()
            load_series.clear()
            st.rerun()
        st.caption("Monthly data from January 1976 where available. Downloads are cached for 24 hours.")
    if start > end:
        st.error("Start month must be on or before end month.")
        st.stop()
    nominal_units = f"{currency_label(c2, countries)} per 1 {currency_label(c1, countries)}"
    st.subheader(f"{countries[c1]} → {countries[c2]}")
    st.caption(f"Nominal S is measured in {nominal_units}. It is never normalized.")
    if c1 == c2:
        st.info("The same country is selected twice: S and RER equal 1 wherever inputs are valid.")

    pieces, metadata, failures = [], {}, []
    with st.spinner("Loading monthly IMF observations…"):
        for label, country, kind in [("P1", c1, "CPI"), ("P2", c2, "CPI"),
                                      ("FX1_LCU_per_USD", c1, "ER"), ("FX2_LCU_per_USD", c2, "ER")]:
            try:
                frame, meta = load_series(country, kind)
                pieces.append(frame.add_prefix(label + "_").rename(columns={label + "_value": label}))
                metadata[label] = meta
                if frame.empty or pd.to_numeric(frame.value, errors="coerce").notna().sum() == 0:
                    st.warning(f"No observations available: {countries[country]} — {kind}.")
                if meta["price_type"] == "HICP":
                    st.info("Euro area prices use the IMF's all-items HICP (harmonised consumer price index). "
                            "The G163 national CPI key is empty. This choice is recorded in the CSV.")
            except (IMFError, ValueError) as exc:
                failures.append((label, str(exc)))
                pieces.append(pd.DataFrame(index=pd.DatetimeIndex([], name="month"), columns=[label]))
    if failures:
        st.error("Some IMF downloads failed. Available series are shown below; missing inputs remain blank. "
                 "Retry with Refresh IMF data. A network failure does not establish that a series is unavailable.")
        with st.expander("Exact errors to copy when requesting help", expanded=True):
            for label, message in failures:
                st.text(f"{label}: {message}")
    inputs = pd.concat(pieces, axis=1)
    sample = calculate_sample(inputs, start, end)
    for label, meta in metadata.items():
        for key, value in meta.items():
            sample[f"{label}_{key}"] = value
    for label, message in failures:
        sample[f"{label}_download_error"] = message
    sample["country1_code"], sample["country2_code"] = c1, c2
    sample["country1_name"], sample["country2_name"] = countries[c1], countries[c2]
    sample["S_units"] = nominal_units
    valid_count = int(sample.valid_RER.sum())
    a, b, c = st.columns(3)
    a.metric("Valid real-rate months", f"{valid_count} / {len(sample)}")
    b.metric("RER* · sample average", f"{sample.RER_star.iloc[0]:.6f}" if valid_count else "Unavailable")
    c.metric("Average real index", f"{sample.Real_Index.mean():.8f}" if valid_count else "Unavailable")
    if valid_count:
        valid_dates = sample.index[sample.valid_RER]
        st.caption(f"Valid RER coverage: {valid_dates.min():%Y-%m} to {valid_dates.max():%Y-%m}. "
                   "Missing interior months, if any, are excluded from the mean.")
    else:
        st.warning("No months have all four positive, finite inputs in this sample. "
                   "Choose another period or country pair. Nominal S can still be shown when both FX inputs exist.")
    if valid_count < len(sample):
        st.caption("Gaps are retained as blank observations. No interpolation, forward filling, or extrapolation is used.")
    st.plotly_chart(build_chart(sample, mode, nominal_units), width="stretch")
    st.caption("Chart zoom changes only the view. Use Start month and End month to change the sample and recalculate RER*.")

    output = sample.copy()
    output.index = output.index.strftime("%Y-%m")
    output.index.name = "month"
    front = ["country1_code", "country2_code", "P1", "P2", "FX1_LCU_per_USD", "FX2_LCU_per_USD",
             "S_C2_per_C1", "RER", "RER_star", "Real_Index", "valid_RER", "sample_start", "sample_end", "S_units"]
    output = output[front + [col for col in output if col not in front]]
    st.download_button("Download selected sample as CSV", output.to_csv(index=True).encode("utf-8-sig"),
                       file_name=f"rer_{c1}_{c2}_{start}_{end}.csv", mime="text/csv")
    with st.expander("Observations and calculations"):
        st.dataframe(output[front], width="stretch")
    if valid_count:
        with st.expander("Verify one observation"):
            row = sample.loc[sample.valid_RER].iloc[0]
            st.write(f"First valid month: {row.name:%Y-%m}")
            st.code(f"S = FX2 / FX1 = {row.FX2_LCU_per_USD:.12g} / {row.FX1_LCU_per_USD:.12g}"
                    f" = {row.S_C2_per_C1:.12g}\n"
                    f"RER = S × P1 / P2 = {row.S_C2_per_C1:.12g} × {row.P1:.12g} / {row.P2:.12g}"
                    f" = {row.RER:.12g}\n"
                    f"Real Index = 100 × RER / RER* = 100 × {row.RER:.12g} / {row.RER_star:.12g}"
                    f" = {row.Real_Index:.12g}", language=None)
            st.caption("Use the CSV's full-precision inputs for your own manual calculation.")
    with st.expander("Method, interpretation, and sources"):
        st.markdown(r"""
Let $E_1$ and $E_2$ denote IMF monthly period-average exchange rates in each country's currency per USD.

$$S_t=E_{2,t}/E_{1,t},\qquad RER_t=S_tP_{1,t}/P_{2,t}.$$

For the selected months with all four positive, finite inputs:

$$RER^*=\frac{1}{N}\sum_t RER_t,\qquad RealIndex_t=100RER_t/RER^*.$$

Each valid month has equal weight. A higher real index represents real appreciation of Country 1
relative to Country 2 under this definition. A value above 100 means above this sample's average;
it is **not** evidence of overvaluation or a purchasing-power-parity equilibrium.

CPI reference years can differ: constant rebasing cancels in the normalized real index.
Currency reforms, series breaks, and changes in coverage can still affect comparisons.
IMF status, scale, reference-period, and other returned attributes are preserved in the download.
The cross-rate is a ratio of monthly average USD rates; it need not equal a monthly average of daily cross-rates.

Sources: [IMF CPI](https://data.imf.org/Datasets/CPI),
[IMF exchange rates](https://data.imf.org/Datasets/ER), and
[IMF API information](https://data.imf.org/en/Resource-Pages/IMF-API).
""")
        for label, meta in metadata.items():
            st.write(f"{label}: {meta['series_key']} · retrieved {meta['retrieved_utc']}")
            st.markdown(f"[IMF request for {label}]({meta['source_url']})")


if __name__ == "__main__":
    main()
