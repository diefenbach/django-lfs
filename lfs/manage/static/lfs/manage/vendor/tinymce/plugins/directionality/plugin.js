/**
 * TinyMCE version 8.0.2 (2025-08-14)
 */

(function () {
    'use strict';

    var global = tinymce.util.Tools.resolve('tinymce.PluginManager');

    /* eslint-disable @typescript-eslint/no-wrapper-object-types */
    const hasProto = (v, constructor, predicate) => {
        var _a;
        if (predicate(v, constructor.prototype)) {
            return true;
        }
        else {
            // String-based fallback time
            return ((_a = v.constructor) === null || _a === void 0 ? void 0 : _a.name) === constructor.name;
        }
    };
    const typeOf = (x) => {
        const t = typeof x;
        if (x === null) {
            return 'null';
        }
        else if (t === 'object' && Array.isArray(x)) {
            return 'array';
        }
        else if (t === 'object' && hasProto(x, String, (o, proto) => proto.isPrototypeOf(o))) {
            return 'string';
        }
        else {
            return t;
        }
    };
    const isType$1 = (type) => (value) => typeOf(value) === type;
    const isSimpleType = (type) => (value) => typeof value === type;
    const isString = isType$1('string');
    const isBoolean = isSimpleType('boolean');
    const isNullable = (a) => a === null || a === undefined;
    const isNonNullable = (a) => !isNullable(a);
    const isFunction = isSimpleType('function');
    const isNumber = isSimpleType('number');

    /** Compose two unary functions. Similar to compose, but avoids using Function.prototype.apply. */
    const compose1 = (fbc, fab) => (a) => fbc(fab(a));
    const constant = (value) => {
        return () => {
            return value;
        };
    };
    const never = constant(false);

    /**
     * The `Optional` type represents a value (of any type) that potentially does
     * not exist. Any `Optional<T>` can either be a `Some<T>` (in which case the
     * value does exist) or a `None` (in which case the value does not exist). This
     * module defines a whole lot of FP-inspired utility functions for dealing with
     * `Optional` objects.
     *
     * Comparison with null or undefined:
     * - We don't get fancy null coalescing operators with `Optional`
     * - We do get fancy helper functions with `Optional`
     * - `Optional` support nesting, and allow for the type to still be nullable (or
     * another `Optional`)
     * - There is no option to turn off strict-optional-checks like there is for
     * strict-null-checks
     */
    class Optional {
        // The internal representation has a `tag` and a `value`, but both are
        // private: able to be console.logged, but not able to be accessed by code
        constructor(tag, value) {
            this.tag = tag;
            this.value = value;
        }
        // --- Identities ---
        /**
         * Creates a new `Optional<T>` that **does** contain a value.
         */
        static some(value) {
            return new Optional(true, value);
        }
        /**
         * Create a new `Optional<T>` that **does not** contain a value. `T` can be
         * any type because we don't actually have a `T`.
         */
        static none() {
            return Optional.singletonNone;
        }
        /**
         * Perform a transform on an `Optional` type. Regardless of whether this
         * `Optional` contains a value or not, `fold` will return a value of type `U`.
         * If this `Optional` does not contain a value, the `U` will be created by
         * calling `onNone`. If this `Optional` does contain a value, the `U` will be
         * created by calling `onSome`.
         *
         * For the FP enthusiasts in the room, this function:
         * 1. Could be used to implement all of the functions below
         * 2. Forms a catamorphism
         */
        fold(onNone, onSome) {
            if (this.tag) {
                return onSome(this.value);
            }
            else {
                return onNone();
            }
        }
        /**
         * Determine if this `Optional` object contains a value.
         */
        isSome() {
            return this.tag;
        }
        /**
         * Determine if this `Optional` object **does not** contain a value.
         */
        isNone() {
            return !this.tag;
        }
        // --- Functor (name stolen from Haskell / maths) ---
        /**
         * Perform a transform on an `Optional` object, **if** there is a value. If
         * you provide a function to turn a T into a U, this is the function you use
         * to turn an `Optional<T>` into an `Optional<U>`. If this **does** contain
         * a value then the output will also contain a value (that value being the
         * output of `mapper(this.value)`), and if this **does not** contain a value
         * then neither will the output.
         */
        map(mapper) {
            if (this.tag) {
                return Optional.some(mapper(this.value));
            }
            else {
                return Optional.none();
            }
        }
        // --- Monad (name stolen from Haskell / maths) ---
        /**
         * Perform a transform on an `Optional` object, **if** there is a value.
         * Unlike `map`, here the transform itself also returns an `Optional`.
         */
        bind(binder) {
            if (this.tag) {
                return binder(this.value);
            }
            else {
                return Optional.none();
            }
        }
        // --- Traversable (name stolen from Haskell / maths) ---
        /**
         * For a given predicate, this function finds out if there **exists** a value
         * inside this `Optional` object that meets the predicate. In practice, this
         * means that for `Optional`s that do not contain a value it returns false (as
         * no predicate-meeting value exists).
         */
        exists(predicate) {
            return this.tag && predicate(this.value);
        }
        /**
         * For a given predicate, this function finds out if **all** the values inside
         * this `Optional` object meet the predicate. In practice, this means that
         * for `Optional`s that do not contain a value it returns true (as all 0
         * objects do meet the predicate).
         */
        forall(predicate) {
            return !this.tag || predicate(this.value);
        }
        filter(predicate) {
            if (!this.tag || predicate(this.value)) {
                return this;
            }
            else {
                return Optional.none();
            }
        }
        // --- Getters ---
        /**
         * Get the value out of the inside of the `Optional` object, using a default
         * `replacement` value if the provided `Optional` object does not contain a
         * value.
         */
        getOr(replacement) {
            return this.tag ? this.value : replacement;
        }
        /**
         * Get the value out of the inside of the `Optional` object, using a default
         * `replacement` value if the provided `Optional` object does not contain a
         * value.  Unlike `getOr`, in this method the `replacement` object is also
         * `Optional` - meaning that this method will always return an `Optional`.
         */
        or(replacement) {
            return this.tag ? this : replacement;
        }
        /**
         * Get the value out of the inside of the `Optional` object, using a default
         * `replacement` value if the provided `Optional` object does not contain a
         * value. Unlike `getOr`, in this method the `replacement` value is
         * "thunked" - that is to say that you don't pass a value to `getOrThunk`, you
         * pass a function which (if called) will **return** the `value` you want to
         * use.
         */
        getOrThunk(thunk) {
            return this.tag ? this.value : thunk();
        }
        /**
         * Get the value out of the inside of the `Optional` object, using a default
         * `replacement` value if the provided Optional object does not contain a
         * value.
         *
         * Unlike `or`, in this method the `replacement` value is "thunked" - that is
         * to say that you don't pass a value to `orThunk`, you pass a function which
         * (if called) will **return** the `value` you want to use.
         *
         * Unlike `getOrThunk`, in this method the `replacement` value is also
         * `Optional`, meaning that this method will always return an `Optional`.
         */
        orThunk(thunk) {
            return this.tag ? this : thunk();
        }
        /**
         * Get the value out of the inside of the `Optional` object, throwing an
         * exception if the provided `Optional` object does not contain a value.
         *
         * WARNING:
         * You should only be using this function if you know that the `Optional`
         * object **is not** empty (otherwise you're throwing exceptions in production
         * code, which is bad).
         *
         * In tests this is more acceptable.
         *
         * Prefer other methods to this, such as `.each`.
         */
        getOrDie(message) {
            if (!this.tag) {
                throw new Error(message !== null && message !== void 0 ? message : 'Called getOrDie on None');
            }
            else {
                return this.value;
            }
        }
        // --- Interop with null and undefined ---
        /**
         * Creates an `Optional` value from a nullable (or undefined-able) input.
         * Null, or undefined, is converted to `None`, and anything else is converted
         * to `Some`.
         */
        static from(value) {
            return isNonNullable(value) ? Optional.some(value) : Optional.none();
        }
        /**
         * Converts an `Optional` to a nullable type, by getting the value if it
         * exists, or returning `null` if it does not.
         */
        getOrNull() {
            return this.tag ? this.value : null;
        }
        /**
         * Converts an `Optional` to an undefined-able type, by getting the value if
         * it exists, or returning `undefined` if it does not.
         */
        getOrUndefined() {
            return this.value;
        }
        // --- Utilities ---
        /**
         * If the `Optional` contains a value, perform an action on that value.
         * Unlike the rest of the methods on this type, `.each` has side-effects. If
         * you want to transform an `Optional<T>` **into** something, then this is not
         * the method for you. If you want to use an `Optional<T>` to **do**
         * something, then this is the method for you - provided you're okay with not
         * doing anything in the case where the `Optional` doesn't have a value inside
         * it. If you're not sure whether your use-case fits into transforming
         * **into** something or **doing** something, check whether it has a return
         * value. If it does, you should be performing a transform.
         */
        each(worker) {
            if (this.tag) {
                worker(this.value);
            }
        }
        /**
         * Turn the `Optional` object into an array that contains all of the values
         * stored inside the `Optional`. In practice, this means the output will have
         * either 0 or 1 elements.
         */
        toArray() {
            return this.tag ? [this.value] : [];
        }
        /**
         * Turn the `Optional` object into a string for debugging or printing. Not
         * recommended for production code, but good for debugging. Also note that
         * these days an `Optional` object can be logged to the console directly, and
         * its inner value (if it exists) will be visible.
         */
        toString() {
            return this.tag ? `some(${this.value})` : 'none()';
        }
    }
    // Sneaky optimisation: every instance of Optional.none is identical, so just
    // reuse the same object
    Optional.singletonNone = new Optional(false);

    const nativeSlice = Array.prototype.slice;
    const map = (xs, f) => {
        // pre-allocating array size when it's guaranteed to be known
        // http://jsperf.com/push-allocated-vs-dynamic/22
        const len = xs.length;
        const r = new Array(len);
        for (let i = 0; i < len; i++) {
            const x = xs[i];
            r[i] = f(x, i);
        }
        return r;
    };
    // Unwound implementing other functions in terms of each.
    // The code size is roughly the same, and it should allow for better optimisation.
    // const each = function<T, U>(xs: T[], f: (x: T, i?: number, xs?: T[]) => void): void {
    const each = (xs, f) => {
        for (let i = 0, len = xs.length; i < len; i++) {
            const x = xs[i];
            f(x, i);
        }
    };
    const filter = (xs, pred) => {
        const r = [];
        for (let i = 0, len = xs.length; i < len; i++) {
            const x = xs[i];
            if (pred(x, i)) {
                r.push(x);
            }
        }
        return r;
    };
    isFunction(Array.from) ? Array.from : (x) => nativeSlice.call(x);

    const fromHtml = (html, scope) => {
        const doc = scope || document;
        const div = doc.createElement('div');
        div.innerHTML = html;
        if (!div.hasChildNodes() || div.childNodes.length > 1) {
            const message = 'HTML does not have a single root node';
            // eslint-disable-next-line no-console
            console.error(message, html);
            throw new Error(message);
        }
        return fromDom(div.childNodes[0]);
    };
    const fromTag = (tag, scope) => {
        const doc = scope || document;
        const node = doc.createElement(tag);
        return fromDom(node);
    };
    const fromText = (text, scope) => {
        const doc = scope || document;
        const node = doc.createTextNode(text);
        return fromDom(node);
    };
    const fromDom = (node) => {
        // TODO: Consider removing this check, but left atm for safety
        if (node === null || node === undefined) {
            throw new Error('Node cannot be null or undefined');
        }
        return {
            dom: node
        };
    };
    const fromPoint = (docElm, x, y) => Optional.from(docElm.dom.elementFromPoint(x, y)).map(fromDom);
    // tslint:disable-next-line:variable-name
    const SugarElement = {
        fromHtml,
        fromTag,
        fromText,
        fromDom,
        fromPoint
    };

    const DOCUMENT_FRAGMENT = 11;
    const ELEMENT = 1;
    const TEXT = 3;

    const is = (element, selector) => {
        const dom = element.dom;
        if (dom.nodeType !== ELEMENT) {
            return false;
        }
        else {
            const elem = dom;
            if (elem.matches !== undefined) {
                return elem.matches(selector);
            }
            else if (elem.msMatchesSelector !== undefined) {
                return elem.msMatchesSelector(selector);
            }
            else if (elem.webkitMatchesSelector !== undefined) {
                return elem.webkitMatchesSelector(selector);
            }
            else if (elem.mozMatchesSelector !== undefined) {
                // cast to any as mozMatchesSelector doesn't exist in TS DOM lib
                return elem.mozMatchesSelector(selector);
            }
            else {
                throw new Error('Browser lacks native selectors');
            } // unfortunately we can't throw this on startup :(
        }
    };

    const name = (element) => {
        const r = element.dom.nodeName;
        return r.toLowerCase();
    };
    const type = (element) => element.dom.nodeType;
    const isType = (t) => (element) => type(element) === t;
    const isElement = isType(ELEMENT);
    const isText = isType(TEXT);
    const isDocumentFragment = isType(DOCUMENT_FRAGMENT);
    const isTag = (tag) => (e) => isElement(e) && name(e) === tag;

    const parent = (element) => Optional.from(element.dom.parentNode).map(SugarElement.fromDom);
    const children$2 = (element) => map(element.dom.childNodes, SugarElement.fromDom);

    /**
     * Is the element a ShadowRoot?
     *
     * Note: this is insufficient to test if any element is a shadow root, but it is sufficient to differentiate between
     * a Document and a ShadowRoot.
     */
    const isShadowRoot = (dos) => isDocumentFragment(dos) && isNonNullable(dos.dom.host);
    const getRootNode = (e) => SugarElement.fromDom(e.dom.getRootNode());
    /** If this element is in a ShadowRoot, return it. */
    const getShadowRoot = (e) => {
        const r = getRootNode(e);
        return isShadowRoot(r) ? Optional.some(r) : Optional.none();
    };
    /** Return the host of a ShadowRoot.
     *
     * This function will throw if Shadow DOM is unsupported in the browser, or if the host is null.
     * If you actually have a ShadowRoot, this shouldn't happen.
     */
    const getShadowHost = (e) => SugarElement.fromDom(e.dom.host);

    const rawSet = (dom, key, value) => {
        /*
         * JQuery coerced everything to a string, and silently did nothing on text node/null/undefined.
         *
         * We fail on those invalid cases, only allowing numbers and booleans.
         */
        if (isString(value) || isBoolean(value) || isNumber(value)) {
            dom.setAttribute(key, value + '');
        }
        else {
            // eslint-disable-next-line no-console
            console.error('Invalid call to Attribute.set. Key ', key, ':: Value ', value, ':: Element ', dom);
            throw new Error('Attribute value was not simple');
        }
    };
    const set = (element, key, value) => {
        rawSet(element.dom, key, value);
    };
    const remove = (element, key) => {
        element.dom.removeAttribute(key);
    };

    // some elements, such as mathml, don't have style attributes
    // others, such as angular elements, have style attributes that aren't a CSSStyleDeclaration
    const isSupported = (dom) => dom.style !== undefined && isFunction(dom.style.getPropertyValue);

    // Node.contains() is very, very, very good performance
    // http://jsperf.com/closest-vs-contains/5
    const inBody = (element) => {
        // Technically this is only required on IE, where contains() returns false for text nodes.
        // But it's cheap enough to run everywhere and Sugar doesn't have platform detection (yet).
        const dom = isText(element) ? element.dom.parentNode : element.dom;
        // use ownerDocument.body to ensure this works inside iframes.
        // Normally contains is bad because an element "contains" itself, but here we want that.
        if (dom === undefined || dom === null || dom.ownerDocument === null) {
            return false;
        }
        const doc = dom.ownerDocument;
        return getShadowRoot(SugarElement.fromDom(dom)).fold(() => doc.body.contains(dom), compose1(inBody, getShadowHost));
    };

    /*
     * NOTE: For certain properties, this returns the "used value" which is subtly different to the "computed value" (despite calling getComputedStyle).
     * Blame CSS 2.0.
     *
     * https://developer.mozilla.org/en-US/docs/Web/CSS/used_value
     */
    const get = (element, property) => {
        const dom = element.dom;
        /*
         * IE9 and above per
         * https://developer.mozilla.org/en/docs/Web/API/window.getComputedStyle
         *
         * Not in numerosity, because it doesn't memoize and looking this up dynamically in performance critical code would be horrendous.
         *
         * JQuery has some magic here for IE popups, but we don't really need that.
         * It also uses element.ownerDocument.defaultView to handle iframes but that hasn't been required since FF 3.6.
         */
        const styles = window.getComputedStyle(dom);
        const r = styles.getPropertyValue(property);
        // jquery-ism: If r is an empty string, check that the element is not in a document. If it isn't, return the raw value.
        // Turns out we do this a lot.
        return (r === '' && !inBody(element)) ? getUnsafeProperty(dom, property) : r;
    };
    // removed: support for dom().style[property] where prop is camel case instead of normal property name
    // empty string is what the browsers (IE11 and Chrome) return when the propertyValue doesn't exists.
    const getUnsafeProperty = (dom, property) => isSupported(dom) ? dom.style.getPropertyValue(property) : '';

    const getDirection = (element) => get(element, 'direction') === 'rtl' ? 'rtl' : 'ltr';

    const ancestor$1 = (scope, predicate, isRoot) => {
        let element = scope.dom;
        const stop = isFunction(isRoot) ? isRoot : never;
        while (element.parentNode) {
            element = element.parentNode;
            const el = SugarElement.fromDom(element);
            if (predicate(el)) {
                return Optional.some(el);
            }
            else if (stop(el)) {
                break;
            }
        }
        return Optional.none();
    };

    const ancestor = (scope, selector, isRoot) => ancestor$1(scope, (e) => is(e, selector), isRoot);

    const children$1 = (scope, predicate) => filter(children$2(scope), predicate);

    const children = (scope, selector) => 
    // It may surprise you to learn this is exactly what JQuery does
    // TODO: Avoid all the wrapping and unwrapping
    children$1(scope, (e) => is(e, selector));

    const getParentElement = (element) => parent(element).filter(isElement);
    // if the block is a list item, we need to get the parent of the list itself
    const getNormalizedBlock = (element, isListItem) => {
        const normalizedElement = isListItem ? ancestor(element, 'ol,ul') : Optional.some(element);
        return normalizedElement.getOr(element);
    };
    const isListItem = isTag('li');
    const setDirOnElements = (dom, blocks, dir) => {
        each(blocks, (block) => {
            const blockElement = SugarElement.fromDom(block);
            const isBlockElementListItem = isListItem(blockElement);
            const normalizedBlock = getNormalizedBlock(blockElement, isBlockElementListItem);
            const normalizedBlockParent = getParentElement(normalizedBlock);
            normalizedBlockParent.each((parent) => {
                // TINY-9314: Remove any inline direction style to ensure that it is only set when necessary and that
                // the dir attribute is favored
                dom.setStyle(normalizedBlock.dom, 'direction', null);
                const parentDirection = getDirection(parent);
                if (parentDirection === dir) {
                    remove(normalizedBlock, 'dir');
                }
                else {
                    set(normalizedBlock, 'dir', dir);
                }
                // TINY-9314: Set an inline direction style if computed css direction is still not as desired. This can
                // happen when the direction style is derived from a stylesheet.
                if (getDirection(normalizedBlock) !== dir) {
                    dom.setStyle(normalizedBlock.dom, 'direction', dir);
                }
                // Remove dir attr and direction style from list children
                if (isBlockElementListItem) {
                    const listItems = children(normalizedBlock, 'li[dir],li[style]');
                    each(listItems, (listItem) => {
                        remove(listItem, 'dir');
                        dom.setStyle(listItem.dom, 'direction', null);
                    });
                }
            });
        });
    };
    const setDir = (editor, dir) => {
        if (editor.selection.isEditable()) {
            setDirOnElements(editor.dom, editor.selection.getSelectedBlocks(), dir);
            editor.nodeChanged();
        }
    };

    const register$1 = (editor) => {
        editor.addCommand('mceDirectionLTR', () => {
            setDir(editor, 'ltr');
        });
        editor.addCommand('mceDirectionRTL', () => {
            setDir(editor, 'rtl');
        });
    };

    const getNodeChangeHandler = (editor, dir) => (api) => {
        const nodeChangeHandler = (e) => {
            const element = SugarElement.fromDom(e.element);
            api.setActive(getDirection(element) === dir);
            api.setEnabled(editor.selection.isEditable());
        };
        editor.on('NodeChange', nodeChangeHandler);
        api.setEnabled(editor.selection.isEditable());
        return () => editor.off('NodeChange', nodeChangeHandler);
    };
    const register = (editor) => {
        editor.ui.registry.addToggleButton('ltr', {
            tooltip: 'Left to right',
            icon: 'ltr',
            onAction: () => editor.execCommand('mceDirectionLTR'),
            onSetup: getNodeChangeHandler(editor, 'ltr')
        });
        editor.ui.registry.addToggleButton('rtl', {
            tooltip: 'Right to left',
            icon: 'rtl',
            onAction: () => editor.execCommand('mceDirectionRTL'),
            onSetup: getNodeChangeHandler(editor, 'rtl')
        });
    };

    var Plugin = () => {
        global.add('directionality', (editor) => {
            register$1(editor);
            register(editor);
        });
    };

    Plugin();
    /** *****
     * DO NOT EXPORT ANYTHING
     *
     * IF YOU DO ROLLUP WILL LEAVE A GLOBAL ON THE PAGE
     *******/

})();
